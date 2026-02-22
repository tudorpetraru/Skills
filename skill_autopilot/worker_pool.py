from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import count
from typing import Callable, Dict, Iterable, List, Sequence

import requests

from .adapters import HostAdapter


@dataclass
class WorkerResult:
    order_index: int
    phase: str
    task: Dict[str, object]
    host: str
    status: str
    output: Dict[str, object]
    error: str | None = None


class DistributedWorkerPool:
    """Dispatches task execution across local adapters and optional remote workers."""

    def __init__(
        self,
        adapters: Dict[str, HostAdapter],
        role_host_map: Dict[str, str],
        max_workers: int = 6,
        remote_worker_endpoints: Sequence[str] | None = None,
    ):
        self.adapters = adapters
        self.role_host_map = role_host_map
        self.max_workers = max_workers
        self.remote_worker_endpoints = list(remote_worker_endpoints or [])
        self._rr = count(0)

    def execute_phase(
        self,
        project_id: str,
        workspace_path: str,
        phase_name: str,
        tasks: Sequence[Dict[str, object]],
        selected_skills: List[str],
        on_result: Callable[[WorkerResult], None] | None = None,
    ) -> List[WorkerResult]:
        if not tasks:
            return []

        results: List[WorkerResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for idx, task in enumerate(tasks, start=1):
                task = dict(task)
                task.setdefault("phase", phase_name)
                host = self._pick_host(task)
                futures.append(
                    executor.submit(
                        self._execute_single,
                        order_index=idx,
                        host=host,
                        project_id=project_id,
                        workspace_path=workspace_path,
                        phase_name=phase_name,
                        task=task,
                        selected_skills=selected_skills,
                    )
                )

            for future in as_completed(futures):
                row = future.result()
                results.append(row)
                if on_result is not None:
                    on_result(row)

        results.sort(key=lambda item: item.order_index)
        return results

    def _pick_host(self, task: Dict[str, object]) -> str:
        role = str(task.get("agent_role", "delivery"))
        preferred = self.role_host_map.get(role)
        if preferred in self.adapters:
            return preferred

        hosts = sorted(self.adapters.keys())
        if not hosts:
            raise RuntimeError("No adapters configured for worker pool")
        index = next(self._rr) % len(hosts)
        return hosts[index]

    def _execute_single(
        self,
        order_index: int,
        host: str,
        project_id: str,
        workspace_path: str,
        phase_name: str,
        task: Dict[str, object],
        selected_skills: List[str],
    ) -> WorkerResult:
        try:
            output = self._execute_via_target(
                host=host,
                project_id=project_id,
                workspace_path=workspace_path,
                task=task,
                selected_skills=selected_skills,
            )
            return WorkerResult(
                order_index=order_index,
                phase=phase_name,
                task=task,
                host=host,
                status="completed",
                output=output,
            )
        except Exception as exc:  # noqa: BLE001
            return WorkerResult(
                order_index=order_index,
                phase=phase_name,
                task=task,
                host=host,
                status="failed",
                output={},
                error=str(exc),
            )

    def _execute_via_target(
        self,
        host: str,
        project_id: str,
        workspace_path: str,
        task: Dict[str, object],
        selected_skills: List[str],
    ) -> Dict[str, object]:
        if self.remote_worker_endpoints:
            endpoint = self.remote_worker_endpoints[next(self._rr) % len(self.remote_worker_endpoints)]
            payload = {
                "host": host,
                "project_id": project_id,
                "workspace_path": workspace_path,
                "task": task,
                "selected_skills": selected_skills,
            }
            response = requests.post(f"{endpoint.rstrip('/')}/execute", json=payload, timeout=180)
            response.raise_for_status()
            return response.json()

        adapter = self.adapters.get(host)
        if not adapter:
            raise RuntimeError(f"No adapter for host={host}")
        return adapter.execute_task(
            project_id=project_id,
            task=task,
            workspace_path=workspace_path,
            selected_skills=selected_skills,
        )
