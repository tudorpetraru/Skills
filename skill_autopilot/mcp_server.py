from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .async_jobs import AsyncJobManager
from .brief_parser import validate_brief_path
from .config import AppConfig, load_config
from .engine import SkillAutopilotEngine
from .models import ApproveGateRequest, EndProjectRequest, RunProjectRequest, StartProjectRequest

SERVER_NAME = "skill-autopilot"
SERVER_INSTRUCTIONS = (
    "Routes project skills from project_brief.md, manages activation lifecycle, "
    "and exposes status/history for desktop agent workflows."
)

mcp = FastMCP(name=SERVER_NAME, instructions=SERVER_INSTRUCTIONS, log_level="WARNING")
_engine: SkillAutopilotEngine | None = None
_jobs = AsyncJobManager(max_workers=6)


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
    auto_run: bool = False,
    auto_approve_gates: bool = True,
    wait_for_run_completion: bool = False,
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
        "execution": _dispatch_or_run(
            project_id=response.project_id,
            auto_approve_gates=auto_approve_gates,
            wait_for_completion=wait_for_run_completion,
        )
        if auto_run
        else None,
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


@mcp.tool(name="sa_validate_brief_path", description="Validate and diagnose project brief path resolution and readability")
def mcp_validate_brief_path(workspace_path: str = "", brief_path: Optional[str] = None) -> Dict[str, Any]:
    if brief_path:
        candidate = brief_path
    elif workspace_path:
        candidate = str(Path(workspace_path) / "project_brief.md")
    else:
        return {"result": {"error": "Provide brief_path or workspace_path"}}
    return {"result": validate_brief_path(candidate)}


@mcp.tool(name="sa_run_project", description="Execute the latest action plan for a project via orchestrator runtime")
def mcp_run_project(project_id: str, auto_approve_gates: bool = True, wait_for_completion: bool = False) -> Dict[str, Any]:
    return _dispatch_or_run(
        project_id=project_id,
        auto_approve_gates=auto_approve_gates,
        wait_for_completion=wait_for_completion,
    )


@mcp.tool(name="sa_task_status", description="Return latest execution run status and per-task outcomes")
def mcp_task_status(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.task_status(project_id).model_dump(mode="json")


@mcp.tool(name="sa_observability_overview", description="Return live health view of active projects with stale/progressing classification")
def mcp_observability_overview(stale_minutes: int = 20, limit: int = 25) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.observability_overview(stale_minutes=stale_minutes, limit=limit)


@mcp.tool(name="sa_project_observability", description="Return detailed observability snapshot for one project")
def mcp_project_observability(project_id: str, task_limit: int = 20, audit_limit: int = 20) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.project_observability(project_id=project_id, task_limit=task_limit, audit_limit=audit_limit)


@mcp.tool(name="sa_reconcile_stale_projects", description="Detect stale projects and optionally close them safely")
def mcp_reconcile_stale_projects(
    stale_minutes: int = 20, close: bool = False, close_reason: str = "paused"
) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.reconcile_stale_projects(stale_minutes=stale_minutes, close=close, close_reason=close_reason)


@mcp.tool(name="sa_approve_gate", description="Approve a blocked gate so execution can continue")
def mcp_approve_gate(project_id: str, gate_id: str, approved_by: str = "human", note: str = "") -> Dict[str, Any]:
    engine = _get_engine()
    result = engine.approve_gate(
        ApproveGateRequest(project_id=project_id, gate_id=gate_id, approved_by=approved_by, note=note)
    )
    return result.model_dump(mode="json")


@mcp.tool(name="sa_job_status", description="Poll background MCP job status for async start/run operations")
def mcp_job_status(job_id: str) -> Dict[str, Any]:
    row = _jobs.get(job_id)
    if row is None:
        return {"job_id": job_id, "status": "not_found"}
    return {
        "job_id": row["job_id"],
        "job_type": row["job_type"],
        "project_id": row["project_id"],
        "status": row["status"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
        "result": row["result"],
        "error": row["error"],
    }


@mcp.tool(name="sa_jobs_recent", description="List recent async MCP jobs for debugging")
def mcp_jobs_recent(limit: int = 20) -> Dict[str, Any]:
    items = []
    for row in _jobs.list_recent(limit=limit):
        items.append(
            {
                "job_id": row["job_id"],
                "job_type": row["job_type"],
                "project_id": row["project_id"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat(),
                "error": row["error"],
            }
        )
    return {"items": items}


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


@mcp.resource(
    "skill-autopilot://observability",
    name="live-observability",
    description="Live summary of active projects and run progress/staleness",
)
def resource_observability() -> str:
    engine = _get_engine()
    data = engine.observability_overview(stale_minutes=20, limit=50)
    lines: List[str] = []
    lines.append("Skill Autopilot Live Observability")
    lines.append(
        f"generated_at={data['generated_at']} active={data['active_project_count']} "
        f"progressing={data['progressing_project_count']} stale={data['stale_project_count']}"
    )
    lines.append("")
    lines.append("project_id | run_status | idle_min | classification | active_skills | workspace")
    lines.append("--- | --- | --- | --- | --- | ---")
    for item in data["items"]:
        lines.append(
            f"{item['project_id']} | {item['run_status']} | {item['idle_minutes']} | "
            f"{item['classification']} | {item['active_skill_count']} | {item['workspace_path']}"
        )
    return "\n".join(lines)


def _dispatch_or_run(project_id: str, auto_approve_gates: bool, wait_for_completion: bool) -> Dict[str, Any]:
    engine = _get_engine()
    if wait_for_completion:
        result = engine.run_project(RunProjectRequest(project_id=project_id, auto_approve_gates=auto_approve_gates))
        return result.model_dump(mode="json")

    def _work() -> Dict[str, Any]:
        out = engine.run_project(RunProjectRequest(project_id=project_id, auto_approve_gates=auto_approve_gates))
        return out.model_dump(mode="json")

    job_id = _jobs.submit(job_type="run_project", fn=_work, project_id=project_id)
    return {"status": "accepted", "job_id": job_id, "project_id": project_id}


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
