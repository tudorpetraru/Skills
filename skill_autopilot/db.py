from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .utils import utc_now


class Database:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path).expanduser())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=30000;")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    workspace_path TEXT NOT NULL,
                    brief_path TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    ended_at TEXT
                );

                CREATE TABLE IF NOT EXISTS routes (
                    route_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    brief_hash TEXT NOT NULL,
                    plan_hash TEXT NOT NULL,
                    snapshot_hash TEXT NOT NULL,
                    selected_skills_json TEXT NOT NULL,
                    rejected_skills_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS plans (
                    plan_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    route_id TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id),
                    FOREIGN KEY(route_id) REFERENCES routes(route_id)
                );

                CREATE TABLE IF NOT EXISTS leases (
                    lease_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    skill_id TEXT NOT NULL,
                    host TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    route_id TEXT,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS project_runs (
                    run_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    route_id TEXT,
                    plan_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id)
                );

                CREATE TABLE IF NOT EXISTS task_runs (
                    task_run_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output_json TEXT NOT NULL,
                    error_text TEXT,
                    order_index INTEGER NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id),
                    FOREIGN KEY(run_id) REFERENCES project_runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS gate_approvals (
                    project_id TEXT NOT NULL,
                    gate_id TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    note TEXT NOT NULL,
                    approved_at TEXT NOT NULL,
                    PRIMARY KEY(project_id, gate_id),
                    FOREIGN KEY(project_id) REFERENCES projects(project_id)
                );
                """
            )

    def upsert_project(self, project_id: str, workspace_path: str, brief_path: str, state: str) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO projects(project_id, workspace_path, brief_path, state, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                  workspace_path=excluded.workspace_path,
                  brief_path=excluded.brief_path,
                  state=excluded.state,
                  updated_at=excluded.updated_at
                """,
                (project_id, workspace_path, brief_path, state, now, now),
            )

    def set_project_state(self, project_id: str, state: str, ended: bool = False) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            if ended:
                conn.execute(
                    "UPDATE projects SET state=?, updated_at=?, ended_at=? WHERE project_id=?",
                    (state, now, now, project_id),
                )
            else:
                conn.execute(
                    "UPDATE projects SET state=?, updated_at=? WHERE project_id=?",
                    (state, now, project_id),
                )

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
            return dict(row) if row else None

    def list_projects(self, limit: int = 25) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def insert_route(
        self,
        route_id: str,
        project_id: str,
        brief_hash: str,
        plan_hash: str,
        snapshot_hash: str,
        selected_skills: Iterable[Dict[str, Any]],
        rejected_skills: Iterable[Dict[str, Any]],
    ) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO routes(route_id, project_id, brief_hash, plan_hash, snapshot_hash,
                                   selected_skills_json, rejected_skills_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    route_id,
                    project_id,
                    brief_hash,
                    plan_hash,
                    snapshot_hash,
                    json.dumps(list(selected_skills), sort_keys=True),
                    json.dumps(list(rejected_skills), sort_keys=True),
                    now,
                ),
            )

    def get_latest_route(self, project_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM routes WHERE project_id=? ORDER BY created_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            return dict(row) if row else None

    def insert_plan(self, plan_id: str, project_id: str, route_id: str, plan_json: Dict[str, Any]) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO plans(plan_id, project_id, route_id, plan_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (plan_id, project_id, route_id, json.dumps(plan_json, sort_keys=True), now),
            )

    def get_latest_plan(self, project_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM plans WHERE project_id=? ORDER BY created_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            if not row:
                return None
            payload = dict(row)
            payload["plan_json"] = json.loads(payload["plan_json"])
            return payload

    def replace_leases(self, project_id: str, leases: Iterable[Dict[str, Any]]) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute("DELETE FROM leases WHERE project_id=?", (project_id,))
            conn.executemany(
                """
                INSERT INTO leases(lease_id, project_id, skill_id, host, expires_at, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        lease["lease_id"],
                        project_id,
                        lease["skill_id"],
                        lease["host"],
                        lease["expires_at"],
                        lease.get("status", "active"),
                        now,
                        now,
                    )
                    for lease in leases
                ],
            )

    def get_active_leases(self, project_id: str | None = None) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM leases WHERE status='active'"
        params: tuple[Any, ...] = ()
        if project_id:
            sql += " AND project_id=?"
            params = (project_id,)
        sql += " ORDER BY expires_at ASC"

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]

    def set_leases_status(self, lease_ids: Iterable[str], status: str) -> None:
        ids = list(lease_ids)
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                f"UPDATE leases SET status=?, updated_at=? WHERE lease_id IN ({placeholders})",
                (status, now, *ids),
            )

    def count_active_skills(self, project_id: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM leases WHERE project_id=? AND status='active'",
                (project_id,),
            ).fetchone()
            return int(row["count"] if row else 0)

    def add_audit_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        project_id: str | None = None,
        route_id: str | None = None,
    ) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_events(project_id, route_id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, route_id, event_type, json.dumps(payload, sort_keys=True), now),
            )

    def get_expired_active_leases(self, now_iso: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM leases WHERE status='active' AND expires_at < ?",
                (now_iso,),
            ).fetchall()
            return [dict(row) for row in rows]

    def create_project_run(self, run_id: str, project_id: str, route_id: str | None, plan_id: str) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO project_runs(run_id, project_id, route_id, plan_id, status, summary_json, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (run_id, project_id, route_id, plan_id, "running", json.dumps({}, sort_keys=True), now),
            )

    def update_project_run(self, run_id: str, status: str, summary: Dict[str, Any]) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE project_runs
                SET status=?, summary_json=?, ended_at=?
                WHERE run_id=?
                """,
                (status, json.dumps(summary, sort_keys=True), now, run_id),
            )

    def get_latest_project_run(self, project_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM project_runs WHERE project_id=? ORDER BY started_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            if not row:
                return None
            payload = dict(row)
            payload["summary_json"] = json.loads(payload["summary_json"])
            return payload

    def insert_task_run(
        self,
        task_run_id: str,
        run_id: str,
        project_id: str,
        phase: str,
        task_id: str,
        title: str,
        agent_role: str,
        status: str,
        output: Dict[str, Any],
        order_index: int,
        error_text: str | None = None,
    ) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO task_runs(
                  task_run_id, run_id, project_id, phase, task_id, title, agent_role,
                  status, output_json, error_text, order_index, started_at, ended_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_run_id,
                    run_id,
                    project_id,
                    phase,
                    task_id,
                    title,
                    agent_role,
                    status,
                    json.dumps(output, sort_keys=True),
                    error_text,
                    order_index,
                    now,
                    now,
                ),
            )

    def list_task_runs(self, run_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM task_runs WHERE run_id=? ORDER BY order_index ASC",
                (run_id,),
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for row in rows:
                payload = dict(row)
                payload["output_json"] = json.loads(payload["output_json"])
                out.append(payload)
            return out

    def upsert_gate_approval(self, project_id: str, gate_id: str, approved_by: str, note: str) -> None:
        now = utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO gate_approvals(project_id, gate_id, approved_by, note, approved_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(project_id, gate_id) DO UPDATE SET
                  approved_by=excluded.approved_by,
                  note=excluded.note,
                  approved_at=excluded.approved_at
                """,
                (project_id, gate_id, approved_by, note, now),
            )

    def is_gate_approved(self, project_id: str, gate_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM gate_approvals WHERE project_id=? AND gate_id=?",
                (project_id, gate_id),
            ).fetchone()
            return row is not None

    def list_gate_approvals(self, project_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM gate_approvals WHERE project_id=? ORDER BY approved_at DESC",
                (project_id,),
            ).fetchall()
            return [dict(row) for row in rows]
