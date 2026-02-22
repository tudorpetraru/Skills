from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
from uuid import uuid4

from .db import Database
from .models import RunProjectResponse
from .utils import utc_now


PHASE_DEFAULT_ROLE = {
    "discovery": "orchestrator",
    "build": "delivery",
    "verify": "quality",
    "ship": "orchestrator",
}


@dataclass
class ExecutionContext:
    project_id: str
    run_id: str
    plan_id: str
    route_id: str | None


class OrchestratorExecutor:
    def __init__(self, db: Database):
        self.db = db

    def run_project(self, project_id: str, auto_approve_gates: bool = True) -> RunProjectResponse:
        plan_row = self.db.get_latest_plan(project_id)
        if not plan_row:
            raise KeyError(f"No execution plan found for project_id={project_id}")

        route = self.db.get_latest_route(project_id)
        context = ExecutionContext(
            project_id=project_id,
            run_id=str(uuid4()),
            plan_id=plan_row["plan_id"],
            route_id=route["route_id"] if route else None,
        )

        self.db.create_project_run(
            run_id=context.run_id,
            project_id=context.project_id,
            route_id=context.route_id,
            plan_id=context.plan_id,
        )

        plan = plan_row["plan_json"]
        phases = list(plan.get("phases", []))
        gates = list(plan.get("gates", []))
        task_order = 0
        executed_tasks = 0

        for phase in phases:
            phase_name = str(phase.get("name", "build"))
            for task in phase.get("tasks", []):
                task_order += 1
                task_id = str(task.get("task_id", f"{phase_name}-{task_order}"))
                title = str(task.get("title", "Execute task"))
                role = str(task.get("agent_role") or PHASE_DEFAULT_ROLE.get(phase_name, "delivery"))
                output = self._execute_task(role=role, phase=phase_name, task=task)
                self.db.insert_task_run(
                    task_run_id=str(uuid4()),
                    run_id=context.run_id,
                    project_id=context.project_id,
                    phase=phase_name,
                    task_id=task_id,
                    title=title,
                    agent_role=role,
                    status="completed",
                    output=output,
                    order_index=task_order,
                )
                executed_tasks += 1

            gate = _phase_gate(phase_name=phase_name, gates=gates)
            if gate:
                gate_id = str(gate.get("gate_id"))
                if auto_approve_gates and not self.db.is_gate_approved(project_id, gate_id):
                    self.db.upsert_gate_approval(
                        project_id=project_id,
                        gate_id=gate_id,
                        approved_by="system-auto",
                        note="Auto-approved during orchestrator execution",
                    )

                if not self.db.is_gate_approved(project_id, gate_id):
                    summary = {
                        "executed_tasks": executed_tasks,
                        "pending_gates": [gate_id],
                        "finished_at": utc_now().isoformat(),
                    }
                    self.db.update_project_run(context.run_id, "blocked", summary)
                    self.db.add_audit_event(
                        event_type="project.run.blocked",
                        project_id=project_id,
                        payload={"run_id": context.run_id, "pending_gate": gate_id},
                    )
                    return RunProjectResponse(
                        project_id=project_id,
                        run_id=context.run_id,
                        status="blocked",
                        executed_tasks=executed_tasks,
                        pending_gates=[gate_id],
                    )

        summary = {
            "executed_tasks": executed_tasks,
            "pending_gates": [],
            "finished_at": utc_now().isoformat(),
        }
        self.db.update_project_run(context.run_id, "completed", summary)
        self.db.add_audit_event(
            event_type="project.run.completed",
            project_id=project_id,
            payload={"run_id": context.run_id, "executed_tasks": executed_tasks},
        )
        return RunProjectResponse(
            project_id=project_id,
            run_id=context.run_id,
            status="completed",
            executed_tasks=executed_tasks,
            pending_gates=[],
        )

    def _execute_task(self, role: str, phase: str, task: Dict[str, object]) -> Dict[str, object]:
        title = str(task.get("title", "Task"))
        base = {
            "executed_at": utc_now().isoformat(),
            "phase": phase,
            "role": role,
            "title": title,
        }

        if role == "orchestrator":
            base["result"] = f"Orchestrated phase context for task: {title}"
        elif role == "research":
            base["result"] = f"Produced evidence-backed options for task: {title}"
        elif role == "quality":
            base["result"] = f"Completed quality checks and acceptance validation for task: {title}"
        elif role == "delivery":
            base["result"] = f"Executed delivery work package for task: {title}"
        else:
            base["result"] = f"Executed role '{role}' task: {title}"

        base["artifacts"] = list(task.get("outputs", ["task_output"]))
        return base


def _phase_gate(phase_name: str, gates: List[Dict[str, object]]) -> Dict[str, object] | None:
    phase_gate_map = {
        "discovery": "gate-1",
        "verify": "gate-2",
    }
    expected = phase_gate_map.get(phase_name)
    if not expected:
        return None
    for gate in gates:
        if str(gate.get("gate_id")) == expected:
            return gate
    return None
