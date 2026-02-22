from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from tkinter import END, Button, Entry, Frame, Label, StringVar, Text, Tk, filedialog, messagebox

import requests
import uvicorn

from .config import load_config, service_url
from .service import app


class ServiceThread(threading.Thread):
    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        self.host = host
        self.port = port

    def run(self) -> None:
        config = uvicorn.Config(app=app, host=self.host, port=self.port, log_level="warning")
        server = uvicorn.Server(config)
        server.run()


class DesktopApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Skill Autopilot")
        self.config = load_config()
        self.base_url = service_url(self.config)
        self.project_id: str | None = None
        self._service_thread: ServiceThread | None = None

        workspace_default = str(Path.cwd())
        self.workspace_var = StringVar(value=workspace_default)
        self.brief_var = StringVar(value=str(Path(workspace_default) / "project_brief.md"))
        self.project_var = StringVar(value="(none)")

        self._build_ui()
        self._ensure_service()

    def _build_ui(self) -> None:
        container = Frame(self.root, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        Label(container, text="Workspace").grid(row=0, column=0, sticky="w")
        Entry(container, textvariable=self.workspace_var, width=70).grid(row=1, column=0, sticky="we", padx=(0, 8))
        Button(container, text="Browse", command=self._browse_workspace).grid(row=1, column=1, sticky="e")

        Label(container, text="Brief File").grid(row=2, column=0, sticky="w", pady=(10, 0))
        Entry(container, textvariable=self.brief_var, width=70).grid(row=3, column=0, sticky="we", padx=(0, 8))

        buttons = Frame(container)
        buttons.grid(row=4, column=0, columnspan=2, sticky="we", pady=(12, 6))
        Button(buttons, text="Start Project", command=self.start_project, width=14).pack(side="left", padx=(0, 8))
        Button(buttons, text="Status", command=self.get_status, width=10).pack(side="left", padx=(0, 8))
        Button(buttons, text="End Project", command=self.end_project, width=12).pack(side="left", padx=(0, 8))
        Button(buttons, text="History", command=self.get_history, width=10).pack(side="left")

        Label(container, text="Current Project").grid(row=5, column=0, sticky="w", pady=(8, 0))
        Label(container, textvariable=self.project_var).grid(row=6, column=0, sticky="w")

        self.output = Text(container, width=90, height=24)
        self.output.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(7, weight=1)

    def _browse_workspace(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.workspace_var.get())
        if not selected:
            return
        self.workspace_var.set(selected)
        self.brief_var.set(str(Path(selected) / "project_brief.md"))

    def _ensure_service(self) -> None:
        if self._service_healthy():
            self._write("Service connected")
            return
        self._service_thread = ServiceThread(self.config.service_host, self.config.service_port)
        self._service_thread.start()
        for _ in range(20):
            if self._service_healthy():
                self._write("Service started")
                try:
                    details = requests.get(f"{self.base_url}/health", timeout=0.8).json()
                    self._write(f"Mode: {details.get('user_mode', 'standard')}")
                except requests.RequestException:
                    pass
                return
            time.sleep(0.2)
        self._write("Service failed to start")

    def _service_healthy(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/health", timeout=0.4)
            return res.status_code == 200
        except requests.RequestException:
            return False

    def _write(self, content: str) -> None:
        self.output.insert(END, content + "\n")
        self.output.see(END)

    def start_project(self) -> None:
        payload = {
            "workspace_path": self.workspace_var.get().strip(),
            "brief_path": self.brief_var.get().strip(),
            "host_targets": ["claude_desktop", "codex_desktop"],
        }
        try:
            res = requests.post(f"{self.base_url}/start-project", json=payload, timeout=15)
            if res.status_code >= 400:
                message = res.json().get("detail", res.text)
                self._write(f"Start failed: {message}")
                return
            data = res.json()
            self.project_id = data["project_id"]
            self.project_var.set(self.project_id)
            self._write("Project started")
            self._write(json.dumps(data, indent=2))
            run_payload = {"project_id": self.project_id, "auto_approve_gates": True}
            run_res = requests.post(f"{self.base_url}/run-project", json=run_payload, timeout=30)
            if run_res.status_code < 400:
                self._write("Execution started")
                self._write(json.dumps(run_res.json(), indent=2))
            else:
                self._write(f"Execution start failed: {run_res.text}")
        except requests.RequestException as exc:
            self._write(f"Start failed: {exc}")

    def get_status(self) -> None:
        if not self.project_id:
            self._write("No active project selected")
            return
        try:
            res = requests.get(f"{self.base_url}/project-status/{self.project_id}", timeout=8)
            if res.status_code >= 400:
                self._write(f"Status failed: {res.text}")
                return
            self._write(json.dumps(res.json(), indent=2))
            task_res = requests.get(f"{self.base_url}/task-status/{self.project_id}", timeout=12)
            if task_res.status_code < 400:
                self._write(json.dumps(task_res.json(), indent=2))
        except requests.RequestException as exc:
            self._write(f"Status failed: {exc}")

    def end_project(self) -> None:
        if not self.project_id:
            self._write("No active project selected")
            return
        payload = {"project_id": self.project_id, "reason": "completed"}
        try:
            res = requests.post(f"{self.base_url}/end-project", json=payload, timeout=12)
            if res.status_code >= 400:
                self._write(f"End failed: {res.text}")
                return
            self._write("Project closed")
            self._write(json.dumps(res.json(), indent=2))
        except requests.RequestException as exc:
            self._write(f"End failed: {exc}")

    def get_history(self) -> None:
        try:
            res = requests.get(f"{self.base_url}/history", timeout=8)
            if res.status_code >= 400:
                self._write(f"History failed: {res.text}")
                return
            self._write(json.dumps(res.json(), indent=2))
        except requests.RequestException as exc:
            self._write(f"History failed: {exc}")


def main() -> None:
    root = Tk()
    app = DesktopApp(root)
    root.geometry("900x700")
    root.mainloop()


if __name__ == "__main__":
    main()
