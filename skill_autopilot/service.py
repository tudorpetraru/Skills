from __future__ import annotations

import argparse
import threading
import time
from contextlib import suppress
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException

from .brief_parser import BriefValidationError
from .config import DEFAULT_CONFIG_PATH, load_config
from .engine import SkillAutopilotEngine
from .models import (
    ApproveGateRequest,
    ApproveGateResponse,
    EndProjectRequest,
    EndProjectResponse,
    GetProjectStatusResponse,
    HealthResponse,
    HistoryEntry,
    RunProjectRequest,
    RunProjectResponse,
    StartProjectRequest,
    StartProjectResponse,
    TaskStatusResponse,
)


class ServiceContainer:
    def __init__(self, config_path: str | None = None):
        path = DEFAULT_CONFIG_PATH if config_path is None else Path(config_path).expanduser()
        config = load_config(path)
        self.engine = SkillAutopilotEngine(config)
        self._stop = threading.Event()
        self._ttl_thread = threading.Thread(target=self._ttl_loop, daemon=True)

    def start_background(self) -> None:
        if not self._ttl_thread.is_alive():
            self._ttl_thread.start()

    def stop(self) -> None:
        self._stop.set()
        with suppress(RuntimeError):
            self.engine.watcher.clear()

    def _ttl_loop(self) -> None:
        while not self._stop.is_set():
            self.engine.sweep_expired()
            self._stop.wait(30)


container = ServiceContainer()
app = FastAPI(title="Skill Autopilot", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    container.start_background()


@app.on_event("shutdown")
def on_shutdown() -> None:
    container.stop()


@app.post("/start-project", response_model=StartProjectResponse)
def start_project(request: StartProjectRequest) -> StartProjectResponse:
    try:
        return container.engine.start_project(request)
    except BriefValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/project-status/{project_id}", response_model=GetProjectStatusResponse)
def project_status(project_id: str) -> GetProjectStatusResponse:
    try:
        return container.engine.get_project_status(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/end-project", response_model=EndProjectResponse)
def end_project(request: EndProjectRequest) -> EndProjectResponse:
    try:
        return container.engine.end_project(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/run-project", response_model=RunProjectResponse)
def run_project(request: RunProjectRequest) -> RunProjectResponse:
    try:
        return container.engine.run_project(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/task-status/{project_id}", response_model=TaskStatusResponse)
def task_status(project_id: str) -> TaskStatusResponse:
    try:
        return container.engine.task_status(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/approve-gate", response_model=ApproveGateResponse)
def approve_gate(request: ApproveGateRequest) -> ApproveGateResponse:
    try:
        return container.engine.approve_gate(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/history", response_model=List[HistoryEntry])
def history() -> List[HistoryEntry]:
    return container.engine.history()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return container.engine.health()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Skill Autopilot service")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--config", default=None)
    parser.add_argument("--reload", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config).expanduser() if args.config else None)
    host = args.host or config.service_host
    port = args.port or config.service_port
    uvicorn.run("skill_autopilot.service:app", host=host, port=port, reload=args.reload)


if __name__ == "__main__":
    main()
