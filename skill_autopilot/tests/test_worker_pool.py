from __future__ import annotations

from pathlib import Path

from skill_autopilot.adapters.mock import MockDesktopAdapter
from skill_autopilot.worker_pool import DistributedWorkerPool


def test_worker_pool_executes_tasks_with_role_host_routing(tmp_path: Path) -> None:
    state_dir = str(tmp_path / "state")
    adapters = {
        "claude_desktop": MockDesktopAdapter("claude_desktop", state_dir=state_dir),
    }
    pool = DistributedWorkerPool(
        adapters=adapters,
        role_host_map={
            "orchestrator": "claude_desktop",
            "delivery": "claude_desktop",
        },
        max_workers=2,
    )

    tasks = [
        {"task_id": "t1", "title": "Orchestrate", "agent_role": "orchestrator", "outputs": ["o1"]},
        {"task_id": "t2", "title": "Deliver", "agent_role": "delivery", "outputs": ["o2"]},
    ]

    results = pool.execute_phase(
        project_id="p1",
        workspace_path=str(tmp_path),
        phase_name="build",
        tasks=tasks,
        selected_skills=["core.orchestrator"],
    )

    assert len(results) == 2
    assert results[0].host == "claude_desktop"
    assert results[1].host == "claude_desktop"
    assert all(item.status == "completed" for item in results)
