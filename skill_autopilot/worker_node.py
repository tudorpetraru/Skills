from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .adapters import MockDesktopAdapter, NativeCliAdapter


class ExecuteRequest(BaseModel):
    host: str
    project_id: str
    workspace_path: str
    task: Dict[str, object]
    selected_skills: List[str] = Field(default_factory=list)


class WorkerNode:
    def __init__(self, mode: str = "native_cli", state_dir: str | None = None):
        state_root = state_dir or str(Path.home() / ".project-skill-router")
        self.adapters = self._build_adapters(mode=mode, state_dir=state_root)

    def _build_adapters(self, mode: str, state_dir: str):
        mode = mode.strip().lower()
        if mode == "native_cli":
            claude_cmd = shutil.which("claude")
            codex_cmd = shutil.which("codex")
            if claude_cmd and codex_cmd:
                return {
                    "claude_desktop": NativeCliAdapter("claude_desktop", state_dir=state_dir, command=claude_cmd),
                    "codex_desktop": NativeCliAdapter("codex_desktop", state_dir=state_dir, command=codex_cmd),
                }
        return {
            "claude_desktop": MockDesktopAdapter("claude_desktop", state_dir=state_dir),
            "codex_desktop": MockDesktopAdapter("codex_desktop", state_dir=state_dir),
        }


node = WorkerNode()
app = FastAPI(title="Skill Autopilot Worker Node", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, object]:
    return {
        "status": "ok",
        "hosts": sorted(node.adapters.keys()),
        "mode": "native_cli" if isinstance(node.adapters.get("claude_desktop"), NativeCliAdapter) else "mock",
    }


@app.post("/execute")
def execute(req: ExecuteRequest) -> Dict[str, object]:
    adapter = node.adapters.get(req.host)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Unknown host: {req.host}")
    try:
        output = adapter.execute_task(
            project_id=req.project_id,
            task=req.task,
            workspace_path=req.workspace_path,
            selected_skills=req.selected_skills,
        )
        return {
            "status": "completed",
            "host": req.host,
            "output": output,
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Skill Autopilot worker node")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument("--mode", choices=["native_cli", "mock"], default="native_cli")
    parser.add_argument("--state-dir", default=str(Path.home() / ".project-skill-router"))
    return parser.parse_args()


def main() -> None:
    global node
    args = parse_args()
    node = WorkerNode(mode=args.mode, state_dir=args.state_dir)
    uvicorn.run("skill_autopilot.worker_node:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
