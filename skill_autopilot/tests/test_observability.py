from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from skill_autopilot.config import AppConfig, CatalogSource
from skill_autopilot.engine import SkillAutopilotEngine
from skill_autopilot.models import StartProjectRequest


def _make_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        db_path=str(tmp_path / "state.db"),
        lease_ttl_hours=1,
        max_active_skills=8,
        adapter_mode="claude_desktop",
        worker_pool_size=1,
        allowlisted_catalogs=[CatalogSource(name="workspace", path=str(tmp_path), pinned_ref="test")],
    )


def _write_brief(path: Path) -> None:
    path.write_text(
        """
# Goals
- Build a project observability feature.
- Keep execution deterministic and auditable.

# Constraints
- Local only.

# Deliverables
- MCP tools and DB-backed status.
""".strip(),
        encoding="utf-8",
    )


def _set_project_updated_at(engine: SkillAutopilotEngine, project_id: str, delta_minutes: int) -> None:
    old = (datetime.now(timezone.utc) - timedelta(minutes=delta_minutes)).isoformat()
    with engine.db._connect() as conn:  # noqa: SLF001 - test helper only
        conn.execute("UPDATE projects SET updated_at=? WHERE project_id=?", (old, project_id))


def test_observability_overview_classifies_stale_project(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)
    engine = SkillAutopilotEngine(_make_config(tmp_path))
    started = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    _set_project_updated_at(engine, started.project_id, delta_minutes=120)
    overview = engine.observability_overview(stale_minutes=10, limit=20)
    target = next(item for item in overview["items"] if item["project_id"] == started.project_id)
    assert target["classification"] == "stale"
    assert target["active_skill_count"] > 0


def test_reconcile_stale_projects_closes_when_requested(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)
    engine = SkillAutopilotEngine(_make_config(tmp_path))
    started = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )
    _set_project_updated_at(engine, started.project_id, delta_minutes=120)

    result = engine.reconcile_stale_projects(stale_minutes=10, close=True, close_reason="paused")
    closed = [item for item in result["closed_projects"] if item["project_id"] == started.project_id]
    assert closed
    assert closed[0]["status"] in {"closed", "partial_close"}

    status = engine.get_project_status(started.project_id)
    assert status.state.value == "closed"
    assert status.active_skill_count == 0


def test_project_observability_contains_task_and_audit_context(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)
    engine = SkillAutopilotEngine(_make_config(tmp_path))
    started = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    # Use the task machine to create a run and complete one task.
    plan = engine.db.get_latest_plan(started.project_id)
    route = engine.db.get_latest_route(started.project_id)
    engine.task_machine.start_run(
        project_id=started.project_id,
        plan_id=plan["plan_id"],
        route_id=route["route_id"],
    )
    first = engine.task_machine.next_task(started.project_id)
    if first and first.get("status") == "ready":
        engine.task_machine.complete_task(
            project_id=started.project_id,
            task_id=str(first["task"]["task_id"]),
            summary="Test task completed",
        )

    out = engine.project_observability(started.project_id, task_limit=10, audit_limit=10)
    assert out["project"]["project_id"] == started.project_id
    assert isinstance(out["recent_tasks"], list)
    assert isinstance(out["recent_audit_events"], list)
    assert isinstance(out["active_leases_by_host"], dict)
