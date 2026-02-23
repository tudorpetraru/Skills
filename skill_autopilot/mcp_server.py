from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .brief_parser import resolve_workspace_path, validate_brief_path
from .config import AppConfig, load_config
from .engine import SkillAutopilotEngine
from .models import ApproveGateRequest, EndProjectRequest, StartProjectRequest

SERVER_NAME = "skill-autopilot"
SERVER_INSTRUCTIONS = (
    "Routes project skills from project_brief.md, manages activation lifecycle, "
    "and exposes a task-by-task execution model for Claude Desktop.\n\n"
    "Workflow:\n"
    "1. Call sa_start_project to create a project. This returns the full task list and deliverables for review — execution does NOT start yet.\n"
    "2. Present the task list and deliverables to the user for approval.\n"
    "3. Once the user approves, call sa_approve_plan to start execution and get the first task.\n"
    "4. Work on the task using the instructions provided. Produce real, concrete files — not just documentation about what to build.\n"
    "5. Call sa_complete_task when done, or sa_skip_task to skip.\n"
    "6. Call sa_next_task to get the next task.\n"
    "7. Repeat until all tasks are complete.\n"
    "8. Call sa_end_project to close the project."
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


# ---------------------------------------------------------------------------
# Core workflow tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="sa_start_project",
    description=(
        "Start a project from a workspace brief. Parses the brief, selects pods and B-kernels, "
        "generates a pod-aware action plan, and returns the task list and deliverables for review. "
        "Execution does NOT start — call sa_approve_plan after user approval to begin."
    ),
)
def mcp_start_project(
    workspace_path: str,
    brief_path: Optional[str] = None,
) -> Dict[str, Any]:
    engine = _get_engine()
    resolved_brief = brief_path or str(Path(workspace_path) / "project_brief.md")
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=workspace_path,
            brief_path=resolved_brief,
            host_targets=["claude_desktop"],
        )
    )
    plan = engine.db.get_latest_plan(response.project_id)
    plan_json = plan["plan_json"] if plan else {}

    # Build plan preview for user approval (do NOT start a run yet).
    task_preview = _format_plan_preview(plan_json)

    return {
        "project_id": response.project_id,
        "status": "pending_approval",
        "plan_id": response.plan_id,
        "industry": plan_json.get("summary", {}).get("industry", ""),
        "kernels": plan_json.get("kernels", []),
        "pods": plan_json.get("pods", []),
        "plan_summary": plan_json.get("summary", {}),
        "task_list": task_preview["task_list"],
        "deliverables": task_preview["deliverables"],
        "task_count": task_preview["task_count"],
        "message": (
            "Plan generated. Present the task list and deliverables to the user for review. "
            "Once approved, call sa_approve_plan to start execution."
        ),
    }


def _format_plan_preview(plan_json: Dict[str, Any]) -> Dict[str, Any]:
    """Format plan phases/tasks/deliverables for user review before approval."""
    phases = plan_json.get("phases", [])
    lines: List[str] = []
    deliverables: List[str] = []
    task_count = 0

    for phase in phases:
        phase_name = phase.get("name", "build")
        lines.append(f"\n## {phase_name.title()}")
        for task in phase.get("tasks", []):
            task_count += 1
            title = task.get("title", task.get("task_id", "?"))
            lines.append(f"  [ ] {title}")
            for output in task.get("outputs", []):
                if output not in deliverables:
                    deliverables.append(output)

    lines.insert(0, f"# Plan Overview: {task_count} tasks")

    if deliverables:
        lines.append("\n## Deliverables")
        for d in deliverables:
            lines.append(f"  - {d}")

    return {
        "task_list": "\n".join(lines),
        "deliverables": deliverables,
        "task_count": task_count,
    }


@mcp.tool(
    name="sa_approve_plan",
    description=(
        "Approve the generated plan and start execution. Call this after the user reviews "
        "the task list from sa_start_project. Returns the first task with full instructions."
    ),
)
def mcp_approve_plan(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    plan = engine.db.get_latest_plan(project_id)
    if not plan:
        return {"project_id": project_id, "status": "error", "message": "No plan found for this project."}

    # Check if a run already exists (idempotency guard).
    existing_run = engine.db.get_latest_project_run(project_id)
    if existing_run:
        # Run already started — just return the next task.
        first_task = engine.task_machine.next_task(project_id)
        checklist = engine.task_machine.task_checklist(project_id)
        return {
            "project_id": project_id,
            "status": "already_started",
            "run_id": existing_run["run_id"],
            "task_list": checklist.get("text", ""),
            "first_task": first_task,
        }

    # Start the run.
    route = engine.db.get_latest_route(project_id)
    run_id = engine.task_machine.start_run(
        project_id=project_id,
        plan_id=plan["plan_id"],
        route_id=route["route_id"] if route else None,
    )
    first_task = engine.task_machine.next_task(project_id)
    checklist = engine.task_machine.task_checklist(project_id)

    engine.db.add_audit_event(
        event_type="plan.approved",
        project_id=project_id,
        payload={"plan_id": plan["plan_id"], "run_id": run_id},
    )

    return {
        "project_id": project_id,
        "status": "started",
        "run_id": run_id,
        "task_list": checklist.get("text", ""),
        "first_task": first_task,
    }


@mcp.tool(
    name="sa_next_task",
    description=(
        "Get the next pending task for a project. Returns the task with full instructions, "
        "pod context, acceptance criteria, and progress. Returns status='all_complete' when done, "
        "or status='blocked' if a gate approval is needed."
    ),
)
def mcp_next_task(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    result = engine.task_machine.next_task(project_id)
    if result is None:
        return {"project_id": project_id, "status": "no_plan", "task_list": ""}
    checklist = result.pop("checklist", {}) or {}
    return {"project_id": project_id, "task_list": checklist.get("text", ""), **result}


@mcp.tool(
    name="sa_complete_task",
    description=(
        "Mark a task as completed with optional summary, artifacts, and evidence. "
        "Returns the next pending task automatically."
    ),
)
def mcp_complete_task(
    project_id: str,
    task_id: str,
    summary: str = "",
    artifacts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    engine = _get_engine()
    result = engine.task_machine.complete_task(
        project_id=project_id,
        task_id=task_id,
        summary=summary,
        artifacts=artifacts or [],
    )
    engine.db.add_audit_event(
        event_type="task.completed",
        project_id=project_id,
        payload={"task_id": task_id, "summary": summary},
    )
    # Lift checklist text from the nested next-task response.
    next_result = result.get("next") or {}
    checklist = next_result.pop("checklist", {}) or {}
    return {"project_id": project_id, "task_list": checklist.get("text", ""), **result}


@mcp.tool(
    name="sa_skip_task",
    description="Skip a task with a reason. Returns the next pending task.",
)
def mcp_skip_task(
    project_id: str,
    task_id: str,
    reason: str = "",
) -> Dict[str, Any]:
    engine = _get_engine()
    result = engine.task_machine.skip_task(
        project_id=project_id,
        task_id=task_id,
        reason=reason,
    )
    engine.db.add_audit_event(
        event_type="task.skipped",
        project_id=project_id,
        payload={"task_id": task_id, "reason": reason},
    )
    next_result = result.get("next") or {}
    checklist = next_result.pop("checklist", {}) or {}
    return {"project_id": project_id, "task_list": checklist.get("text", ""), **result}


# ---------------------------------------------------------------------------
# Existing lifecycle tools
# ---------------------------------------------------------------------------


@mcp.tool(name="sa_project_status", description="Get current project lifecycle state and active host footprint")
def mcp_project_status(project_id: str) -> Dict[str, Any]:
    engine = _get_engine()
    status = engine.get_project_status(project_id)
    return status.model_dump(mode="json")


@mcp.tool(name="sa_reroute_project", description="Reroute active project skills after brief changes")
def mcp_reroute_project(project_id: str, force: bool = False) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.reroute_project(project_id=project_id, force=force)


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


@mcp.tool(name="sa_validate_brief_path", description="Validate and diagnose project brief path resolution")
def mcp_validate_brief_path(workspace_path: str = "", brief_path: Optional[str] = None) -> Dict[str, Any]:
    if brief_path:
        candidate = brief_path
    elif workspace_path:
        candidate = str(Path(workspace_path) / "project_brief.md")
    else:
        return {"result": {"error": "Provide brief_path or workspace_path"}}
    return {"result": validate_brief_path(candidate)}


@mcp.tool(name="sa_task_status", description="Return latest execution run status and per-task outcomes")
def mcp_task_status(project_id: str, task_limit: int = 50, include_outputs: bool = False) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.task_status(
        project_id=project_id,
        task_limit=max(1, min(task_limit, 500)),
        include_outputs=include_outputs,
    ).model_dump(mode="json")


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


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


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
