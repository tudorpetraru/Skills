from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .config import AppConfig, load_config
from .engine import SkillAutopilotEngine
from .models import EndProjectRequest, StartProjectRequest

SERVER_NAME = "skill-autopilot"
SERVER_INSTRUCTIONS = (
    "Routes project skills from project_brief.md, manages activation lifecycle, "
    "and exposes status/history for desktop agent workflows."
)

mcp = FastMCP(name=SERVER_NAME, instructions=SERVER_INSTRUCTIONS, log_level="WARNING")
_engine: SkillAutopilotEngine | None = None


def _make_engine(config_path: Optional[str] = None) -> SkillAutopilotEngine:
    config = load_config(Path(config_path).expanduser() if config_path else None)
    return SkillAutopilotEngine(config)


def _get_engine() -> SkillAutopilotEngine:
    global _engine
    if _engine is None:
        _engine = _make_engine()
    return _engine


@mcp.tool(name="sa_start_project", description="Start a project from a workspace brief and activate selected skills")
def mcp_start_project(
    workspace_path: str,
    brief_path: Optional[str] = None,
    host_targets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    engine = _get_engine()
    resolved_brief = brief_path or str(Path(workspace_path) / "project_brief.md")
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=workspace_path,
            brief_path=resolved_brief,
            host_targets=host_targets or ["claude_desktop", "codex_desktop"],
        )
    )
    plan = engine.db.get_latest_plan(response.project_id)
    return {
        "project_id": response.project_id,
        "status": response.status,
        "plan_id": response.plan_id,
        "selected_skills": [item.model_dump() for item in response.selected_skills],
        "action_plan": plan["plan_json"] if plan else None,
    }


@mcp.tool(name="sa_project_status", description="Get current project lifecycle state and active host footprint")
def mcp_project_status(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    status = engine.get_project_status(project_id)
    return status.model_dump(mode="json")


@mcp.tool(name="sa_reroute_project", description="Reroute active project skills after brief changes")
def mcp_reroute_project(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    changed = engine.reroute_if_material_change(project_id)
    route = engine.db.get_latest_route(project_id)
    plan = engine.db.get_latest_plan(project_id)
    return {
        "project_id": project_id,
        "rerouted": changed,
        "latest_route_id": route["route_id"] if route else None,
        "latest_plan_id": plan["plan_id"] if plan else None,
    }


@mcp.tool(name="sa_end_project", description="End an active project and deactivate all skill leases")
def mcp_end_project(project_id: str, reason: str = "completed") -> Dict[str, Any]:
    engine = _get_engine()
    response = engine.end_project(EndProjectRequest(project_id=project_id, reason=reason))
    return response.model_dump(mode="json")


@mcp.tool(name="sa_project_history", description="List recent projects and their state summaries")
def mcp_project_history(limit: int = 20) -> Dict[str, Any]:
    engine = _get_engine()
    items = [entry.model_dump(mode="json") for entry in engine.history()[: max(1, min(limit, 100))]]
    return {"items": items}


@mcp.tool(name="sa_active_plan", description="Return latest generated action plan for a project")
def mcp_active_plan(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    plan = engine.db.get_latest_plan(project_id)
    if not plan:
        return {"project_id": project_id, "plan": None}
    return {"project_id": project_id, "plan": plan["plan_json"], "plan_id": plan["plan_id"]}


@mcp.tool(name="sa_service_health", description="Show local service health and routing policy mode")
def mcp_service_health() -> Dict[str, Any]:
    engine = _get_engine()
    return engine.health().model_dump(mode="json")


@mcp.resource("skill-autopilot://policy", name="routing-policy", description="Current effective local routing policy")
def resource_policy() -> str:
    engine = _get_engine()
    config: AppConfig = engine.config
    return (
        f"admin_mode={config.admin_mode}\n"
        f"max_active_skills={config.max_active_skills}\n"
        f"min_relevance_score={config.min_relevance_score}\n"
        f"max_utility_skills={config.max_utility_skills}\n"
        f"max_skills_per_cluster={config.max_skills_per_cluster}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Skill Autopilot MCP server")
    parser.add_argument("--config", default=None, help="Path to config TOML")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="MCP transport. Use stdio for Claude desktop integration.",
    )
    return parser.parse_args()


def main() -> None:
    global _engine
    args = parse_args()
    _engine = _make_engine(args.config)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
