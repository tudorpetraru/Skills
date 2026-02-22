from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .base import HostAdapter
from ..models import AdapterResult


class MockDesktopAdapter(HostAdapter):
    """Local adapter used for prototype lifecycle behavior.

    State is persisted in a local text file to emulate host activation footprint.
    """

    def __init__(self, host: str, state_dir: str):
        self.host = host
        self.state_file = Path(state_dir).expanduser() / f"{host}_active_skills.txt"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def capability_profile(self) -> Dict[str, object]:
        return {
            "host": self.host,
            "supports_activate": True,
            "supports_deactivate": True,
            "max_skills": 50,
        }

    def activate(self, project_id: str, skill_ids: List[str]) -> AdapterResult:
        try:
            existing = self._read_lines()
            to_write = sorted(set(existing + [f"{project_id}:{skill}" for skill in skill_ids]))
            self.state_file.write_text("\n".join(to_write), encoding="utf-8")
            return AdapterResult(host=self.host, success=True, message=f"Activated {len(skill_ids)} skills")
        except OSError as exc:
            return AdapterResult(host=self.host, success=False, message=str(exc))

    def deactivate(self, project_id: str, skill_ids: List[str]) -> AdapterResult:
        try:
            existing = self._read_lines()
            block = {f"{project_id}:{skill}" for skill in skill_ids}
            remaining = [line for line in existing if line not in block]
            self.state_file.write_text("\n".join(remaining), encoding="utf-8")
            return AdapterResult(host=self.host, success=True, message=f"Deactivated {len(skill_ids)} skills")
        except OSError as exc:
            return AdapterResult(host=self.host, success=False, message=str(exc))

    def _read_lines(self) -> List[str]:
        if not self.state_file.exists():
            return []
        return [line.strip() for line in self.state_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    def execute_task(
        self,
        project_id: str,
        task: Dict[str, object],
        workspace_path: str,
        selected_skills: List[str],
    ) -> Dict[str, object]:
        title = str(task.get("title", "Task"))
        return {
            "project_id": project_id,
            "host": self.host,
            "mode": "mock",
            "title": title,
            "workspace_path": workspace_path,
            "selected_skill_count": len(selected_skills),
            "result": f"Mock execution completed for: {title}",
        }
