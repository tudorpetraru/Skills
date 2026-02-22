from __future__ import annotations

import time
from pathlib import Path

from skill_autopilot.async_jobs import AsyncJobManager


def test_async_job_manager_success() -> None:
    jobs = AsyncJobManager(max_workers=1)
    job_id = jobs.submit("unit", lambda: {"ok": True})
    for _ in range(50):
        row = jobs.get(job_id)
        assert row is not None
        if row["status"] == "succeeded":
            assert row["result"] == {"ok": True}
            assert row["error"] is None
            return
        time.sleep(0.01)
    raise AssertionError("job did not complete")


def test_async_job_manager_failure() -> None:
    jobs = AsyncJobManager(max_workers=1)

    def _boom():
        raise RuntimeError("boom")

    job_id = jobs.submit("unit", _boom)
    for _ in range(50):
        row = jobs.get(job_id)
        assert row is not None
        if row["status"] == "failed":
            assert "RuntimeError" in (row["error"] or "")
            return
        time.sleep(0.01)
    raise AssertionError("job did not fail as expected")


def test_async_job_manager_persists_state_across_restart(tmp_path: Path) -> None:
    state_file = tmp_path / "mcp_jobs.json"
    jobs = AsyncJobManager(max_workers=1, state_file=str(state_file))
    job_id = jobs.submit("unit", lambda: {"ok": True}, project_id="p1")
    for _ in range(100):
        row = jobs.get(job_id)
        assert row is not None
        if row["status"] == "succeeded":
            break
        time.sleep(0.01)

    restarted = AsyncJobManager(max_workers=1, state_file=str(state_file))
    row = restarted.get(job_id)
    assert row is not None
    assert row["status"] == "succeeded"
    assert row["project_id"] == "p1"
