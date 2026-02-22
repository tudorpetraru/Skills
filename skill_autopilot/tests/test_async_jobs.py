from __future__ import annotations

import time

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
