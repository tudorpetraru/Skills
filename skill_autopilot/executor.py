"""Task state machine executor.

Replaces the subprocess-spawning executor with a stateful task tracker.
Claude Desktop works through tasks via sa_next_task / sa_complete_task MCP calls.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from uuid import uuid4

from .db import Database
from .models import TaskState
from .utils import utc_now


PHASE_ORDER = ["discovery", "build", "verify", "ship"]


class TaskStateMachine:
    """Manages task lifecycle for a project run.

    Tasks flow: pending → active → completed/skipped/failed.
    """

    def __init__(self, db: Database):
        self.db = db

    def start_run(self, project_id: str, plan_id: str, route_id: str | None = None) -> str:
        """Create a new project run and initialize task records from the plan."""
        run_id = str(uuid4())
        plan_row = self.db.get_plan(plan_id)
        if not plan_row:
            raise KeyError(f"plan_id not found: {plan_id}")

        plan = plan_row["plan_json"]
        phases = plan.get("phases", [])
        total_tasks = sum(len(phase.get("tasks", [])) for phase in phases)

        self.db.create_project_run(
            run_id=run_id,
            project_id=project_id,
            route_id=route_id,
            plan_id=plan_id,
        )
        self.db.update_project_run(
            run_id,
            "running",
            {
                "planned_tasks": total_tasks,
                "executed_tasks": 0,
                "failed_tasks": 0,
                "current_phase": "pending",
                "pending_gates": [],
            },
            ended=False,
        )
        return run_id

    def task_checklist(self, project_id: str, current_task_id: str | None = None) -> Dict[str, object]:
        """Return all tasks across all phases with completion status.

        Each task is annotated with:
          - status: "completed", "skipped", "current", "pending", "blocked"
          - marker: "[x]", "[~]", "[→]", "[ ]", "[!]"
        Also returns a formatted text block for easy display.
        """
        plan_row = self.db.get_latest_plan(project_id)
        if not plan_row:
            return {"phases": [], "text": "No plan found."}

        plan = plan_row["plan_json"]
        run = self.db.get_latest_project_run(project_id)

        # Build status map from task runs.
        status_map: Dict[str, str] = {}
        if run:
            task_runs = self.db.list_task_runs(run["run_id"], limit=500)
            for tr in task_runs:
                status_map[tr["task_id"]] = tr.get("status", "completed")

        phases_out: List[Dict[str, object]] = []
        lines: List[str] = []
        found_current = False

        for phase in plan.get("phases", []):
            phase_name = str(phase.get("name", "build"))
            phase_tasks: List[Dict[str, object]] = []

            # Check if phase is gated.
            gate = self._phase_gate(phase_name, plan.get("gates", []))
            phase_blocked = False
            if gate:
                gate_id = str(gate.get("gate_id"))
                if not self.db.is_gate_approved(project_id, gate_id):
                    phase_blocked = True

            lines.append(f"\n## {phase_name.title()}")

            for task in phase.get("tasks", []):
                task_id = str(task.get("task_id", ""))
                title = str(task.get("title", task_id))
                db_status = status_map.get(task_id)

                if db_status == "completed":
                    marker = "[x]"
                    status = "completed"
                elif db_status == "skipped":
                    marker = "[~]"
                    status = "skipped"
                elif phase_blocked and not found_current:
                    marker = "[!]"
                    status = "blocked"
                elif task_id == current_task_id or (not found_current and db_status is None):
                    marker = "[→]"
                    status = "current"
                    found_current = True
                else:
                    marker = "[ ]"
                    status = "pending"

                lines.append(f"  {marker} {title}")
                phase_tasks.append({
                    "task_id": task_id,
                    "title": title,
                    "status": status,
                    "marker": marker,
                })

            phases_out.append({"phase": phase_name, "tasks": phase_tasks})

        # Summary line.
        total = sum(len(p["tasks"]) for p in phases_out)
        done = sum(1 for p in phases_out for t in p["tasks"] if t["status"] in ("completed", "skipped"))
        lines.insert(0, f"# Task Progress: {done}/{total} complete")

        return {
            "phases": phases_out,
            "completed": done,
            "total": total,
            "text": "\n".join(lines),
        }

    def next_task(self, project_id: str) -> Optional[Dict[str, object]]:
        """Return the next pending task with full instruction context.

        Returns None if all tasks are completed or the project has no plan.
        """
        plan_row = self.db.get_latest_plan(project_id)
        if not plan_row:
            return None

        plan = plan_row["plan_json"]
        run = self.db.get_latest_project_run(project_id)
        completed_ids = set()
        if run:
            task_runs = self.db.list_task_runs(run["run_id"], limit=500)
            completed_ids = {
                tr["task_id"]
                for tr in task_runs
                if tr.get("status") in ("completed", "skipped")
            }

        # Walk phases in order, find first pending task.
        for phase in plan.get("phases", []):
            phase_name = phase.get("name", "build")
            for task in phase.get("tasks", []):
                task_id = str(task.get("task_id", ""))
                if task_id in completed_ids:
                    continue

                # Check gate: is the previous phase's gate approved?
                gate = self._phase_gate(phase_name, plan.get("gates", []))
                if gate:
                    gate_id = str(gate.get("gate_id"))
                    if not self.db.is_gate_approved(project_id, gate_id):
                        return {
                            "status": "blocked",
                            "blocked_by_gate": gate_id,
                            "gate_criteria": gate.get("criteria", []),
                            "message": f"Phase '{phase_name}' is blocked by gate '{gate_id}'. Approve it to continue.",
                            "checklist": self.task_checklist(project_id, task_id),
                        }

                return {
                    "status": "ready",
                    "task": task,
                    "phase": phase_name,
                    "progress": {
                        "completed": len(completed_ids),
                        "total": sum(len(p.get("tasks", [])) for p in plan.get("phases", [])),
                        "current_phase": phase_name,
                    },
                    "checklist": self.task_checklist(project_id, task_id),
                }

        # All tasks done.
        return {
            "status": "all_complete",
            "progress": {
                "completed": len(completed_ids),
                "total": sum(len(p.get("tasks", [])) for p in plan.get("phases", [])),
            },
            "checklist": self.task_checklist(project_id),
        }

    def complete_task(
        self,
        project_id: str,
        task_id: str,
        summary: str = "",
        artifacts: List[str] | None = None,
        evidence: Dict[str, object] | None = None,
    ) -> Dict[str, object]:
        """Mark a task as completed and return the next task."""
        run = self.db.get_latest_project_run(project_id)
        if not run:
            raise KeyError(f"No active run for project {project_id}")

        self.db.insert_task_run(
            task_run_id=str(uuid4()),
            run_id=run["run_id"],
            project_id=project_id,
            phase=self._task_phase(project_id, task_id),
            task_id=task_id,
            title=summary or task_id,
            agent_role="claude_desktop",
            status="completed",
            output={
                "summary": summary,
                "artifacts": artifacts or [],
                "evidence": evidence or {},
            },
            order_index=self._next_order_index(run["run_id"]),
        )

        # Update run summary.
        self._update_run_summary(run["run_id"], project_id)

        # Auto-approve gates if we finished a phase.
        self._auto_approve_phase_gates(project_id, task_id)

        # Get next task.
        next_task = self.next_task(project_id)

        # If all complete, mark run as completed.
        if next_task and next_task.get("status") == "all_complete":
            summary_data = run.get("summary_json") or {}
            summary_data = dict(summary_data)
            summary_data["finished_at"] = utc_now().isoformat()
            self.db.update_project_run(run["run_id"], "completed", summary_data, ended=True)

        return {
            "completed_task_id": task_id,
            "next": next_task,
        }

    def skip_task(
        self,
        project_id: str,
        task_id: str,
        reason: str = "",
    ) -> Dict[str, object]:
        """Mark a task as skipped and return the next task."""
        run = self.db.get_latest_project_run(project_id)
        if not run:
            raise KeyError(f"No active run for project {project_id}")

        self.db.insert_task_run(
            task_run_id=str(uuid4()),
            run_id=run["run_id"],
            project_id=project_id,
            phase=self._task_phase(project_id, task_id),
            task_id=task_id,
            title=f"Skipped: {reason}" if reason else f"Skipped: {task_id}",
            agent_role="claude_desktop",
            status="skipped",
            output={"reason": reason},
            order_index=self._next_order_index(run["run_id"]),
        )
        self._update_run_summary(run["run_id"], project_id)
        return {
            "skipped_task_id": task_id,
            "reason": reason,
            "next": self.next_task(project_id),
        }

    def _task_phase(self, project_id: str, task_id: str) -> str:
        """Look up which phase a task belongs to."""
        plan_row = self.db.get_latest_plan(project_id)
        if plan_row:
            for phase in plan_row["plan_json"].get("phases", []):
                for task in phase.get("tasks", []):
                    if str(task.get("task_id")) == task_id:
                        return str(phase.get("name", "build"))
        return "build"

    def _next_order_index(self, run_id: str) -> int:
        task_runs = self.db.list_task_runs(run_id, limit=500)
        return len(task_runs) + 1

    def _update_run_summary(self, run_id: str, project_id: str) -> None:
        task_runs = self.db.list_task_runs(run_id, limit=500)
        completed = sum(1 for tr in task_runs if tr.get("status") == "completed")
        skipped = sum(1 for tr in task_runs if tr.get("status") == "skipped")
        failed = sum(1 for tr in task_runs if tr.get("status") == "failed")

        plan_row = self.db.get_latest_plan(project_id)
        total = 0
        current_phase = "build"
        if plan_row:
            phases = plan_row["plan_json"].get("phases", [])
            total = sum(len(p.get("tasks", [])) for p in phases)
            # Determine current phase from progress.
            done_ids = {tr["task_id"] for tr in task_runs if tr.get("status") in ("completed", "skipped")}
            for phase in phases:
                for task in phase.get("tasks", []):
                    if str(task.get("task_id")) not in done_ids:
                        current_phase = str(phase.get("name", "build"))
                        break
                else:
                    continue
                break

        self.db.update_project_run(
            run_id,
            "running",
            {
                "planned_tasks": total,
                "executed_tasks": completed,
                "skipped_tasks": skipped,
                "failed_tasks": failed,
                "current_phase": current_phase,
                "pending_gates": [],
            },
            ended=False,
        )

    def _phase_gate(self, phase_name: str, gates: List[Dict[str, object]]) -> Dict[str, object] | None:
        phase_gate_map = {
            "build": "gate-1",     # Discovery must be reviewed before build.
            "ship": "gate-2",      # Quality must be checked before ship.
        }
        expected = phase_gate_map.get(phase_name)
        if not expected:
            return None
        for gate in gates:
            if str(gate.get("gate_id")) == expected:
                return gate
        return None

    def _auto_approve_phase_gates(self, project_id: str, completed_task_id: str) -> None:
        """Auto-approve phase gates when all tasks in the gated phase are done."""
        plan_row = self.db.get_latest_plan(project_id)
        if not plan_row:
            return

        run = self.db.get_latest_project_run(project_id)
        if not run:
            return

        task_runs = self.db.list_task_runs(run["run_id"], limit=500)
        done_ids = {tr["task_id"] for tr in task_runs if tr.get("status") in ("completed", "skipped")}
        plan = plan_row["plan_json"]

        # Check if the discovery phase is complete → auto-approve gate-1.
        # Check if the verify phase is complete → auto-approve gate-2.
        gate_phase_map = {
            "gate-1": "discovery",
            "gate-2": "verify",
        }
        for gate_id, phase_name in gate_phase_map.items():
            if self.db.is_gate_approved(project_id, gate_id):
                continue
            for phase in plan.get("phases", []):
                if phase.get("name") != phase_name:
                    continue
                phase_task_ids = {str(t.get("task_id")) for t in phase.get("tasks", [])}
                if phase_task_ids and phase_task_ids.issubset(done_ids):
                    self.db.upsert_gate_approval(
                        project_id=project_id,
                        gate_id=gate_id,
                        approved_by="system-auto",
                        note=f"All {phase_name} tasks completed",
                    )
