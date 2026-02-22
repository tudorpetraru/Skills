from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from typing import Any, Callable, Dict, Optional
from uuid import uuid4

from .utils import utc_now


class AsyncJobManager:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="sa-job")
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def submit(self, job_type: str, fn: Callable[[], Any], project_id: str | None = None) -> str:
        job_id = str(uuid4())
        now = utc_now()
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "job_type": job_type,
                "project_id": project_id,
                "status": "queued",
                "created_at": now,
                "updated_at": now,
                "result": None,
                "error": None,
            }
        self._executor.submit(self._run, job_id, fn)
        return job_id

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return dict(job)

    def list_recent(self, limit: int = 20) -> list[Dict[str, Any]]:
        with self._lock:
            jobs = list(self._jobs.values())
        jobs.sort(key=lambda item: item["updated_at"], reverse=True)
        return [dict(item) for item in jobs[: max(1, min(limit, 200))]]

    def _run(self, job_id: str, fn: Callable[[], Any]) -> None:
        self._update(job_id, status="running")
        try:
            result = fn()
            self._update(job_id, status="succeeded", result=_to_json_compatible(result), error=None)
        except Exception as exc:  # noqa: BLE001
            self._update(job_id, status="failed", error=f"{type(exc).__name__}: {exc}")

    def _update(
        self,
        job_id: str,
        *,
        status: str | None = None,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        with self._lock:
            row = self._jobs.get(job_id)
            if row is None:
                return
            if status is not None:
                row["status"] = status
            if result is not None:
                row["result"] = result
            if error is not None or status == "succeeded":
                row["error"] = error
            row["updated_at"] = utc_now()


def _to_json_compatible(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _to_json_compatible(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_compatible(v) for v in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _to_json_compatible(model_dump(mode="json"))
    return str(value)

