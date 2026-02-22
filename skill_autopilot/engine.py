from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional
from uuid import uuid4

from .adapters import MockDesktopAdapter
from .brief_parser import BriefValidationError, is_material_change, parse_brief
from .catalog import load_catalog
from .config import AppConfig
from .db import Database
from .decomposer import decompose_project
from .executor import OrchestratorExecutor
from .lease_manager import LeaseManager
from .models import (
    ApproveGateRequest,
    ApproveGateResponse,
    EndProjectRequest,
    EndProjectResponse,
    GetProjectStatusResponse,
    HealthResponse,
    HistoryEntry,
    ProjectState,
    RunProjectRequest,
    RunProjectResponse,
    RoutingPolicy,
    StartProjectRequest,
    StartProjectResponse,
    TaskStatusResponse,
)
from .router import route_skills
from .utils import utc_now
from .watcher import BriefWatcherRegistry


class SkillAutopilotEngine:
    def __init__(self, config: AppConfig):
        self.config = config
        self.db = Database(config.db_path)
        state_dir = str(Path(config.db_path).expanduser().parent)
        self.adapters = {
            "claude_desktop": MockDesktopAdapter("claude_desktop", state_dir=state_dir),
            "codex_desktop": MockDesktopAdapter("codex_desktop", state_dir=state_dir),
        }
        self.lease_manager = LeaseManager(db=self.db, adapters=self.adapters, ttl_hours=config.lease_ttl_hours)
        self.executor = OrchestratorExecutor(self.db)
        self.watcher = BriefWatcherRegistry()
        self._intent_cache: Dict[str, object] = {}
        self._lock = Lock()
        self._last_snapshot_hash: Optional[str] = None

    def start_project(self, request: StartProjectRequest) -> StartProjectResponse:
        with self._lock:
            project_id = str(uuid4())
            intent, brief_hash = parse_brief(request.brief_path)
            skills, snapshot_hash = load_catalog(self.config.allowlisted_catalogs)
            self._last_snapshot_hash = snapshot_hash

            policy = RoutingPolicy(
                max_active_skills=self.config.max_active_skills,
                lease_ttl_hours=self.config.lease_ttl_hours,
                min_relevance_score=self.config.min_relevance_score,
                max_utility_skills=self.config.max_utility_skills,
                max_skills_per_cluster=self.config.max_skills_per_cluster,
                utility_penalty=self.config.utility_penalty,
                preferred_sources=self.config.preferred_sources,
                preferred_source_bonus=self.config.preferred_source_bonus,
            )
            route = route_skills(
                intent=intent,
                catalog=skills,
                host_targets=request.host_targets,
                policy=policy,
                snapshot_hash=snapshot_hash,
            )

            plan_payload = decompose_project(intent, route.selected_skills)
            plan_id = str(uuid4())

            self.db.upsert_project(
                project_id=project_id,
                workspace_path=request.workspace_path,
                brief_path=request.brief_path,
                state=ProjectState.ACTIVE.value,
            )
            self.db.insert_route(
                route_id=route.route_id,
                project_id=project_id,
                brief_hash=brief_hash,
                plan_hash=route.plan_hash,
                snapshot_hash=route.snapshot_hash,
                selected_skills=[item.model_dump() for item in route.selected_skills],
                rejected_skills=[item.model_dump() for item in route.rejected_skills],
            )
            self.db.insert_plan(plan_id=plan_id, project_id=project_id, route_id=route.route_id, plan_json=plan_payload)
            self.lease_manager.activate_project_skills(
                project_id=project_id,
                hosts=request.host_targets,
                selected_skills=route.selected_skills,
            )

            self._intent_cache[project_id] = intent
            self.db.add_audit_event(
                event_type="project.start",
                project_id=project_id,
                route_id=route.route_id,
                payload={
                    "workspace_path": request.workspace_path,
                    "brief_path": request.brief_path,
                    "host_targets": request.host_targets,
                    "selected_skill_count": len(route.selected_skills),
                    "rejected_skill_count": len(route.rejected_skills),
                },
            )

            self._attach_watcher(project_id, request)

            return StartProjectResponse(
                project_id=project_id,
                selected_skills=route.selected_skills,
                plan_id=plan_id,
                status="started",
            )

    def reroute_if_material_change(self, project_id: str) -> bool:
        with self._lock:
            project = self.db.get_project(project_id)
            if not project or project["state"] != ProjectState.ACTIVE.value:
                return False

            request = StartProjectRequest(
                workspace_path=project["workspace_path"],
                brief_path=project["brief_path"],
                host_targets=self._active_hosts(project_id),
            )

            new_intent, brief_hash = parse_brief(request.brief_path)
            old_intent = self._intent_cache.get(project_id)
            if old_intent is not None and not is_material_change(old_intent, new_intent):
                self.db.add_audit_event(
                    event_type="project.reroute.skipped",
                    project_id=project_id,
                    payload={"reason": "non_material_change"},
                )
                return False

            skills, snapshot_hash = load_catalog(self.config.allowlisted_catalogs)
            self._last_snapshot_hash = snapshot_hash
            route = route_skills(
                intent=new_intent,
                catalog=skills,
                host_targets=request.host_targets,
                policy=RoutingPolicy(
                    max_active_skills=self.config.max_active_skills,
                    lease_ttl_hours=self.config.lease_ttl_hours,
                    min_relevance_score=self.config.min_relevance_score,
                    max_utility_skills=self.config.max_utility_skills,
                    max_skills_per_cluster=self.config.max_skills_per_cluster,
                    utility_penalty=self.config.utility_penalty,
                    preferred_sources=self.config.preferred_sources,
                    preferred_source_bonus=self.config.preferred_source_bonus,
                ),
                snapshot_hash=snapshot_hash,
            )

            plan_payload = decompose_project(new_intent, route.selected_skills)
            plan_id = str(uuid4())

            self.db.insert_route(
                route_id=route.route_id,
                project_id=project_id,
                brief_hash=brief_hash,
                plan_hash=route.plan_hash,
                snapshot_hash=route.snapshot_hash,
                selected_skills=[item.model_dump() for item in route.selected_skills],
                rejected_skills=[item.model_dump() for item in route.rejected_skills],
            )
            self.db.insert_plan(plan_id=plan_id, project_id=project_id, route_id=route.route_id, plan_json=plan_payload)

            # Replace leases to reflect rerouted skill set.
            self.lease_manager.activate_project_skills(
                project_id=project_id,
                hosts=request.host_targets,
                selected_skills=route.selected_skills,
            )

            self._intent_cache[project_id] = new_intent
            self.db.add_audit_event(
                event_type="project.reroute.applied",
                project_id=project_id,
                route_id=route.route_id,
                payload={"plan_id": plan_id, "selected_skill_count": len(route.selected_skills)},
            )
            return True

    def end_project(self, request: EndProjectRequest) -> EndProjectResponse:
        with self._lock:
            self.db.set_project_state(request.project_id, ProjectState.CLOSING.value)
            response = self.lease_manager.deactivate_project(project_id=request.project_id, reason=request.reason.value)
            ended = response.status in {"closed", "partial_close"}
            state = ProjectState.CLOSED.value if ended else ProjectState.ERROR.value
            self.db.set_project_state(request.project_id, state, ended=ended)
            self.watcher.remove(request.project_id)
            self._intent_cache.pop(request.project_id, None)
            return response

    def run_project(self, request: RunProjectRequest) -> RunProjectResponse:
        with self._lock:
            project = self.db.get_project(request.project_id)
            if not project:
                raise KeyError(f"project_id not found: {request.project_id}")
            if project["state"] not in {ProjectState.ACTIVE.value, ProjectState.CLOSING.value}:
                raise ValueError(f"project is not executable in state={project['state']}")

            result = self.executor.run_project(
                project_id=request.project_id,
                auto_approve_gates=request.auto_approve_gates,
            )
            self.db.add_audit_event(
                event_type="project.run.requested",
                project_id=request.project_id,
                payload=result.model_dump(mode="json"),
            )
            return result

    def approve_gate(self, request: ApproveGateRequest) -> ApproveGateResponse:
        with self._lock:
            project = self.db.get_project(request.project_id)
            if not project:
                raise KeyError(f"project_id not found: {request.project_id}")
            self.db.upsert_gate_approval(
                project_id=request.project_id,
                gate_id=request.gate_id,
                approved_by=request.approved_by,
                note=request.note,
            )
            self.db.add_audit_event(
                event_type="project.gate.approved",
                project_id=request.project_id,
                payload={
                    "gate_id": request.gate_id,
                    "approved_by": request.approved_by,
                    "note": request.note,
                },
            )
            return ApproveGateResponse(
                project_id=request.project_id,
                gate_id=request.gate_id,
                approved=True,
                approved_by=request.approved_by,
            )

    def task_status(self, project_id: str) -> TaskStatusResponse:
        project = self.db.get_project(project_id)
        if not project:
            raise KeyError(f"project_id not found: {project_id}")
        run = self.db.get_latest_project_run(project_id)
        if not run:
            return TaskStatusResponse(project_id=project_id, status="not_started", executed_tasks=0, tasks=[], approvals=[])
        tasks = self.db.list_task_runs(run["run_id"])
        approvals = self.db.list_gate_approvals(project_id)
        return TaskStatusResponse(
            project_id=project_id,
            run_id=run["run_id"],
            status=run["status"],
            executed_tasks=len(tasks),
            tasks=tasks,
            approvals=approvals,
        )

    def get_project_status(self, project_id: str) -> GetProjectStatusResponse:
        project = self.db.get_project(project_id)
        if not project:
            raise KeyError(f"project_id not found: {project_id}")
        route = self.db.get_latest_route(project_id)

        return GetProjectStatusResponse(
            project_id=project_id,
            state=ProjectState(project["state"]),
            active_hosts=self._active_hosts(project_id),
            active_skill_count=self.db.count_active_skills(project_id),
            last_route_at=route["created_at"] if route else None,
        )

    def history(self) -> List[HistoryEntry]:
        rows = self.db.list_projects(limit=50)
        entries: List[HistoryEntry] = []
        for row in rows:
            entries.append(
                HistoryEntry(
                    project_id=row["project_id"],
                    workspace_path=row["workspace_path"],
                    state=ProjectState(row["state"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    selected_skill_count=self.db.count_active_skills(row["project_id"]),
                )
            )
        return entries

    def health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            db_path=self.db.db_path,
            service_time=utc_now(),
            last_snapshot_hash=self._last_snapshot_hash,
            user_mode="admin" if self.config.admin_mode else "standard",
        )

    def sweep_expired(self) -> List[str]:
        expired_project_ids = self.lease_manager.sweep_expired_leases()
        for project_id in expired_project_ids:
            self.watcher.remove(project_id)
            self._intent_cache.pop(project_id, None)
        return expired_project_ids

    def _attach_watcher(self, project_id: str, request: StartProjectRequest) -> None:
        if not self.watcher.supports_watch():
            self.db.add_audit_event(
                event_type="watcher.disabled",
                project_id=project_id,
                payload={"reason": "watchdog_unavailable"},
            )
            return

        def _callback() -> None:
            try:
                rerouted = self.reroute_if_material_change(project_id)
                self.db.add_audit_event(
                    event_type="watcher.trigger",
                    project_id=project_id,
                    payload={"rerouted": rerouted},
                )
            except BriefValidationError as exc:
                self.db.add_audit_event(
                    event_type="watcher.error",
                    project_id=project_id,
                    payload={"error": str(exc)},
                )

        self.watcher.add(project_id=project_id, brief_path=request.brief_path, callback=_callback)

    def _active_hosts(self, project_id: str) -> List[str]:
        leases = self.db.get_active_leases(project_id=project_id)
        return sorted({lease["host"] for lease in leases})
