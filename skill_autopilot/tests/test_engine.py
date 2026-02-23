from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from skill_autopilot.brief_parser import BriefValidationError, parse_brief
from skill_autopilot.catalog import load_catalog
from skill_autopilot.config import AppConfig, CatalogSource
from skill_autopilot.engine import SkillAutopilotEngine
from skill_autopilot.models import (
    ApproveGateRequest,
    EndProjectRequest,
    SkillMetadata,
    StartProjectRequest,
)
from skill_autopilot.router import route_skills


def _make_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        db_path=str(tmp_path / "state.db"),
        lease_ttl_hours=1,
        max_active_skills=8,
        adapter_mode="claude_desktop",
        worker_pool_size=1,
        allowlisted_catalogs=[CatalogSource(name="workspace", path=str(tmp_path), pinned_ref="test")],
    )


def _write_brief(path: Path, extra: str = "") -> None:
    path.write_text(
        """
# Goals
- Build a software planning system for project delivery.
- Ensure auditable decisions and quality gates.

# Constraints
- Keep setup simple for non technical users.
- Run locally with deterministic behavior.

# Deliverables
- Working desktop shell.
- Background service with API.
""".strip()
        + "\n"
        + extra,
        encoding="utf-8",
    )


def test_start_project_success(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    assert response.status == "started"
    assert response.project_id
    assert len(response.selected_skills) > 0

    status = engine.get_project_status(response.project_id)
    assert status.state.value == "active"
    assert status.active_skill_count > 0


def test_invalid_brief_rejected(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    brief.write_text("too short", encoding="utf-8")

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    with pytest.raises(BriefValidationError):
        engine.start_project(
            StartProjectRequest(
                workspace_path=str(tmp_path),
                brief_path=str(brief),
                host_targets=["claude_desktop"],
            )
        )


def test_reroute_material_change(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    _write_brief(brief, extra="\n# Constraints\n- New strict compliance policy and audit needs.")
    result = engine.reroute_project(response.project_id)
    assert result["rerouted"] is True
    assert result["reason"] == "material_change"


def test_reroute_non_material_with_force(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)
    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    skipped = engine.reroute_project(response.project_id, force=False)
    assert skipped["rerouted"] is False
    assert skipped["reason"] == "non_material_change"

    forced = engine.reroute_project(response.project_id, force=True)
    assert forced["rerouted"] is True
    assert forced["reason"] == "forced"


def test_end_project_deactivates_leases(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    closed = engine.end_project(EndProjectRequest(project_id=response.project_id, reason="completed"))
    assert closed.status in {"closed", "partial_close"}

    status = engine.get_project_status(response.project_id)
    assert status.active_skill_count == 0


def test_end_project_terminates_running_runs(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )
    route = engine.db.get_latest_route(response.project_id)
    run_id = str(uuid4())
    engine.db.create_project_run(
        run_id=run_id,
        project_id=response.project_id,
        route_id=route["route_id"] if route else None,
        plan_id=response.plan_id,
    )

    closed = engine.end_project(EndProjectRequest(project_id=response.project_id, reason="completed"))
    assert closed.status in {"closed", "partial_close"}

    run = engine.db.get_latest_project_run(response.project_id)
    assert run is not None
    assert run["status"] == "failed"
    assert run["summary_json"].get("terminated_by") == "end_project"


def test_route_determinism(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    intent, _ = parse_brief(str(brief))
    config = _make_config(tmp_path)
    skills, snapshot = load_catalog(config.allowlisted_catalogs)

    route_a = route_skills(intent, skills, ["claude_desktop"], policy=config_to_policy(config), snapshot_hash=snapshot)
    route_b = route_skills(intent, skills, ["claude_desktop"], policy=config_to_policy(config), snapshot_hash=snapshot)

    assert route_a.plan_hash == route_b.plan_hash
    assert [s.skill_id for s in route_a.selected_skills] == [s.skill_id for s in route_b.selected_skills]


def config_to_policy(config: AppConfig):
    from skill_autopilot.models import RoutingPolicy

    return RoutingPolicy(
        max_active_skills=config.max_active_skills,
        lease_ttl_hours=config.lease_ttl_hours,
        min_relevance_score=config.min_relevance_score,
        max_utility_skills=config.max_utility_skills,
        max_skills_per_cluster=config.max_skills_per_cluster,
        utility_penalty=config.utility_penalty,
    )


def test_route_filters_system_and_limits_utilities(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)
    intent, _ = parse_brief(str(brief))

    catalog = [
        SkillMetadata(
            skill_id=".system.skill-installer",
            name="System Skill Installer",
            description="Installs skills",
            tags=["utility"],
            source_repo="test",
            pinned_ref="x",
        ),
        SkillMetadata(
            skill_id="pdf",
            name="PDF",
            description="Work with PDFs",
            tags=["utility", "pdf"],
            source_repo="test",
            pinned_ref="x",
        ),
        SkillMetadata(
            skill_id="screenshot",
            name="Screenshot",
            description="Capture screenshots",
            tags=["utility", "image"],
            source_repo="test",
            pinned_ref="x",
        ),
        SkillMetadata(
            skill_id="core.orchestrator",
            name="Orchestrator",
            description="Coordinate delivery",
            tags=["planning", "delivery"],
            source_repo="test",
            pinned_ref="x",
        ),
    ]

    policy = config_to_policy(_make_config(tmp_path))
    route = route_skills(intent, catalog, ["claude_desktop"], policy=policy, snapshot_hash="snap")
    selected = {item.skill_id for item in route.selected_skills}
    rejected = {item.skill_id: item.reason for item in route.rejected_skills}

    assert ".system.skill-installer" not in selected
    assert rejected[".system.skill-installer"] == "excluded by policy"
    assert len(selected & {"pdf", "screenshot"}) <= 1


def test_route_allows_explicit_utility_request(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief, extra="\nNeed screenshot evidence for UI validation.")
    intent, _ = parse_brief(str(brief))

    catalog = [
        SkillMetadata(
            skill_id="screenshot",
            name="Screenshot",
            description="Capture screenshots",
            tags=["utility", "image"],
            source_repo="test",
            pinned_ref="x",
        ),
        SkillMetadata(
            skill_id="core.orchestrator",
            name="Orchestrator",
            description="Coordinate delivery",
            tags=["planning", "delivery"],
            source_repo="test",
            pinned_ref="x",
        ),
    ]

    policy = config_to_policy(_make_config(tmp_path))
    route = route_skills(intent, catalog, ["claude_desktop"], policy=policy, snapshot_hash="snap")
    selected = {item.skill_id for item in route.selected_skills}
    assert "screenshot" in selected


def test_route_does_not_treat_generic_web_term_as_utility_request(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief, extra="\nConstraint: no separate web UI.")
    intent, _ = parse_brief(str(brief))

    catalog = [
        SkillMetadata(
            skill_id="screenshot",
            name="Screenshot",
            description="Capture screenshots",
            tags=["utility", "image"],
            source_repo="test",
            pinned_ref="x",
        ),
        SkillMetadata(
            skill_id="core.orchestrator",
            name="Orchestrator",
            description="Coordinate delivery",
            tags=["planning", "delivery"],
            source_repo="test",
            pinned_ref="x",
        ),
    ]

    policy = config_to_policy(_make_config(tmp_path))
    route = route_skills(intent, catalog, ["claude_desktop"], policy=policy, snapshot_hash="snap")
    selected = {item.skill_id for item in route.selected_skills}
    assert "screenshot" not in selected


def test_catalog_reads_frontmatter_and_dependencies(tmp_path: Path) -> None:
    skill_dir = tmp_path / "library" / "skills" / "core" / "planner"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """
---
name: Planner Skill
description: Plans execution from normalized requirements.
tags: [planning, delivery]
hosts: [claude_desktop]
dependencies: [core.orchestrator, core.quality]
---

# Planner Skill
Hosts: claude_desktop
Tags: planning,delivery
Depends-On: core.orchestrator,core.quality
""".strip(),
        encoding="utf-8",
    )

    skills, _ = load_catalog([CatalogSource(name="local_library", path=str(tmp_path / "library" / "skills"), pinned_ref="x")])
    planner = [skill for skill in skills if skill.skill_id == "core.planner"][0]
    assert planner.name == "Planner Skill"
    assert "planning" in planner.tags
    assert set(planner.dependencies) >= {"core.orchestrator", "core.quality"}


def test_route_prefers_local_library_source(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)
    intent, _ = parse_brief(str(brief))

    local = SkillMetadata(
        skill_id="discovery.local_option",
        name="Local Option",
        description="software planning system deterministic delivery",
        tags=["software", "planning", "delivery"],
        source_repo="local_library",
        pinned_ref="x",
    )
    external = SkillMetadata(
        skill_id="discovery.external_option",
        name="External Option",
        description="software planning system deterministic delivery",
        tags=["software", "planning", "delivery"],
        source_repo="external",
        pinned_ref="x",
    )

    policy = config_to_policy(_make_config(tmp_path))
    policy.max_active_skills = 1
    route = route_skills(intent, [external, local], ["claude_desktop"], policy=policy, snapshot_hash="snap")
    assert route.selected_skills[0].skill_id == "discovery.local_option"


def test_catalog_avoids_duplicate_loading_from_nested_sources(tmp_path: Path) -> None:
    library_root = tmp_path / "library" / "skills"
    nested_skill_dir = library_root / "core" / "planner"
    nested_skill_dir.mkdir(parents=True)
    (nested_skill_dir / "SKILL.md").write_text(
        """
---
name: Planner
description: Planner skill.
tags: [planning]
---
# Planner
""".strip(),
        encoding="utf-8",
    )

    skills, _ = load_catalog(
        [
            CatalogSource(name="workspace_skills", path=str(tmp_path), pinned_ref="workspace"),
            CatalogSource(name="local_library", path=str(library_root), pinned_ref="local-v1"),
        ]
    )
    planner_ids = [skill.skill_id for skill in skills if "planner" in skill.skill_id]
    assert planner_ids == ["core.planner"]


def test_task_machine_next_complete_flow(tmp_path: Path) -> None:
    """Test the sa_next_task / sa_complete_task flow via the task state machine."""
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    # Start a run.
    plan = engine.db.get_latest_plan(response.project_id)
    route = engine.db.get_latest_route(response.project_id)
    run_id = engine.task_machine.start_run(
        project_id=response.project_id,
        plan_id=plan["plan_id"],
        route_id=route["route_id"],
    )
    assert run_id

    # Get first task.
    first = engine.task_machine.next_task(response.project_id)
    assert first is not None
    assert first["status"] == "ready"
    assert "task" in first
    task = first["task"]
    assert task["task_id"]
    assert task["phase"] == "discovery"

    # Complete it.
    result = engine.task_machine.complete_task(
        project_id=response.project_id,
        task_id=str(task["task_id"]),
        summary="Scope document produced",
    )
    assert result["completed_task_id"] == str(task["task_id"])
    assert result["next"] is not None

    # Complete all remaining tasks to reach 'all_complete'.
    max_iterations = 50
    for _ in range(max_iterations):
        next_result = engine.task_machine.next_task(response.project_id)
        if next_result is None or next_result.get("status") == "all_complete":
            break
        if next_result.get("status") == "blocked":
            engine.approve_gate(
                ApproveGateRequest(
                    project_id=response.project_id,
                    gate_id=next_result["blocked_by_gate"],
                    approved_by="test",
                )
            )
            continue
        task = next_result["task"]
        engine.task_machine.complete_task(
            project_id=response.project_id,
            task_id=str(task["task_id"]),
            summary=f"Completed {task['task_id']}",
        )
    else:
        pytest.fail("Did not reach all_complete within max iterations")

    final = engine.task_machine.next_task(response.project_id)
    assert final is not None
    assert final["status"] == "all_complete"


def test_task_machine_skip(tmp_path: Path) -> None:
    """Test that skipping a task advances to the next one."""
    brief = tmp_path / "project_brief.md"
    _write_brief(brief)

    engine = SkillAutopilotEngine(_make_config(tmp_path))
    response = engine.start_project(
        StartProjectRequest(
            workspace_path=str(tmp_path),
            brief_path=str(brief),
            host_targets=["claude_desktop"],
        )
    )

    plan = engine.db.get_latest_plan(response.project_id)
    route = engine.db.get_latest_route(response.project_id)
    engine.task_machine.start_run(
        project_id=response.project_id,
        plan_id=plan["plan_id"],
        route_id=route["route_id"],
    )

    first = engine.task_machine.next_task(response.project_id)
    assert first["status"] == "ready"
    task_id = str(first["task"]["task_id"])

    result = engine.task_machine.skip_task(
        project_id=response.project_id,
        task_id=task_id,
        reason="Not needed for this project",
    )
    assert result["skipped_task_id"] == task_id
    assert result["next"] is not None
    # The next task should be different from the skipped one.
    if result["next"]["status"] == "ready":
        assert str(result["next"]["task"]["task_id"]) != task_id
