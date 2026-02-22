from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

from ..brief_parser import resolve_workspace_path
from .mock import MockDesktopAdapter


class NativeCliAdapter(MockDesktopAdapter):
    """Native host adapter that executes tasks through installed host CLIs.

    Supported hosts:
    - claude_desktop -> `claude -p --output-format json ...`
    - codex_desktop -> `codex exec --output-last-message ...`
    """

    def __init__(self, host: str, state_dir: str, command: str, timeout_seconds: int = 120):
        super().__init__(host=host, state_dir=state_dir)
        self.command = command
        self.timeout_seconds = timeout_seconds

    def capability_profile(self) -> Dict[str, object]:
        base = super().capability_profile()
        base.update(
            {
                "mode": "native_cli",
                "command": self.command,
                "supports_execute": True,
            }
        )
        return base

    def execute_task(
        self,
        project_id: str,
        task: Dict[str, object],
        workspace_path: str,
        selected_skills: List[str],
    ) -> Dict[str, object]:
        if self.host == "claude_desktop":
            return self._execute_with_claude(project_id, task, workspace_path, selected_skills)
        if self.host == "codex_desktop":
            return self._execute_with_codex(project_id, task, workspace_path, selected_skills)
        return super().execute_task(project_id, task, workspace_path, selected_skills)

    def _execute_with_claude(
        self,
        project_id: str,
        task: Dict[str, object],
        workspace_path: str,
        selected_skills: List[str],
    ) -> Dict[str, object]:
        resolved_workspace = _resolve_workspace_for_host(workspace_path)
        prompt = _task_prompt(project_id=project_id, task=task, selected_skills=selected_skills)
        cmd = [
            self.command,
            "-p",
            "--output-format",
            "json",
            "--add-dir",
            resolved_workspace,
            "--",
            prompt,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_seconds)
        if proc.returncode != 0:
            raise RuntimeError(f"claude task execution failed: {proc.stderr[:300]}")

        payload = json.loads(proc.stdout.strip() or "{}")
        return {
            "host": self.host,
            "mode": "native_cli",
            "command": self.command,
            "result": payload.get("result", ""),
            "usage": payload.get("usage", {}),
            "raw": payload,
        }

    def _execute_with_codex(
        self,
        project_id: str,
        task: Dict[str, object],
        workspace_path: str,
        selected_skills: List[str],
    ) -> Dict[str, object]:
        resolved_workspace = _resolve_workspace_for_host(workspace_path)
        prompt = _task_prompt(project_id=project_id, task=task, selected_skills=selected_skills)
        with tempfile.NamedTemporaryFile(prefix="codex_last_", suffix=".txt", delete=False) as fp:
            output_path = fp.name

        cmd = [
            self.command,
            "exec",
            "--skip-git-repo-check",
            "--cd",
            resolved_workspace,
            "--output-last-message",
            output_path,
            prompt,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_seconds)
        if proc.returncode != 0:
            raise RuntimeError(f"codex task execution failed: {proc.stderr[:300]}")

        result = ""
        path = Path(output_path)
        if path.exists():
            result = path.read_text(encoding="utf-8").strip()
            path.unlink(missing_ok=True)

        return {
            "host": self.host,
            "mode": "native_cli",
            "command": self.command,
            "result": result,
            "stderr": proc.stderr[-1000:],
        }


def _task_prompt(project_id: str, task: Dict[str, object], selected_skills: List[str]) -> str:
    return (
        "You are executing one project task in Skill Autopilot.\n"
        f"project_id: {project_id}\n"
        f"task_id: {task.get('task_id','task')}\n"
        f"title: {task.get('title','Task')}\n"
        f"phase: {task.get('phase','build')}\n"
        f"agent_role: {task.get('agent_role','delivery')}\n"
        f"inputs: {json.dumps(task.get('inputs', []), ensure_ascii=True)}\n"
        f"outputs: {json.dumps(task.get('outputs', []), ensure_ascii=True)}\n"
        f"acceptance_checks: {json.dumps(task.get('acceptance_checks', []), ensure_ascii=True)}\n"
        f"active_skills: {json.dumps(selected_skills, ensure_ascii=True)}\n\n"
        "Respond with concise JSON object containing keys: summary, artifacts, risks."
    )


def _resolve_workspace_for_host(workspace_path: str) -> str:
    diag = resolve_workspace_path(workspace_path)
    if diag.get("exists") and diag.get("is_dir"):
        return str(diag.get("resolved_path"))
    note = str(diag.get("resolution_note") or "workspace path unresolved")
    raise RuntimeError(
        "workspace path is not accessible to host CLI: "
        f"{workspace_path} ({note}). "
        "If running from a VM/session path, set SKILL_AUTOPILOT_PATH_MAPS."
    )
