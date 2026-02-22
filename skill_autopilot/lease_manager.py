from __future__ import annotations

from datetime import timedelta
from typing import Dict, Iterable, List, Sequence, Tuple
from uuid import uuid4

from .adapters import HostAdapter
from .db import Database
from .models import EndProjectResponse, SkillReason
from .utils import utc_now


class LeaseManager:
    def __init__(self, db: Database, adapters: Dict[str, HostAdapter], ttl_hours: int):
        self.db = db
        self.adapters = adapters
        self.ttl_hours = ttl_hours

    def activate_project_skills(self, project_id: str, hosts: Sequence[str], selected_skills: Sequence[SkillReason]) -> None:
        expires_at = (utc_now() + timedelta(hours=self.ttl_hours)).isoformat()
        skill_ids = [skill.skill_id for skill in selected_skills]

        # Always clear existing project activations first to avoid stale skills
        # when rerouting to a different active set.
        existing = self.db.get_active_leases(project_id=project_id)
        grouped_existing: Dict[str, List[str]] = {}
        for lease in existing:
            grouped_existing.setdefault(lease["host"], []).append(lease["skill_id"])

        for host, old_skill_ids in grouped_existing.items():
            adapter = self.adapters.get(host)
            if not adapter:
                continue
            result = adapter.deactivate(project_id=project_id, skill_ids=sorted(set(old_skill_ids)))
            self.db.add_audit_event(
                event_type="adapter.deactivate.pre_activate",
                project_id=project_id,
                payload={
                    "host": host,
                    "success": result.success,
                    "message": result.message,
                    "skill_count": len(set(old_skill_ids)),
                },
            )

        leases = []
        for host in hosts:
            adapter = self.adapters[host]
            result = adapter.activate(project_id=project_id, skill_ids=skill_ids)
            self.db.add_audit_event(
                event_type="adapter.activate",
                project_id=project_id,
                payload={"host": host, "success": result.success, "message": result.message, "skill_count": len(skill_ids)},
            )
            for skill_id in skill_ids:
                leases.append(
                    {
                        "lease_id": str(uuid4()),
                        "project_id": project_id,
                        "skill_id": skill_id,
                        "host": host,
                        "expires_at": expires_at,
                        "status": "active",
                    }
                )

        self.db.replace_leases(project_id, leases)

    def deactivate_project(self, project_id: str, reason: str) -> EndProjectResponse:
        active = self.db.get_active_leases(project_id=project_id)
        if not active:
            self.db.add_audit_event(
                event_type="project.close",
                project_id=project_id,
                payload={"reason": reason, "deactivated": 0, "status": "closed"},
            )
            return EndProjectResponse(project_id=project_id, deactivated_skills=0, status="closed")

        grouped: Dict[str, List[str]] = {}
        for lease in active:
            grouped.setdefault(lease["host"], []).append(lease["skill_id"])

        failed_hosts: List[str] = []
        for host, skill_ids in grouped.items():
            adapter = self.adapters.get(host)
            if not adapter:
                failed_hosts.append(host)
                continue
            result = adapter.deactivate(project_id=project_id, skill_ids=sorted(set(skill_ids)))
            if not result.success:
                failed_hosts.append(host)
            self.db.add_audit_event(
                event_type="adapter.deactivate",
                project_id=project_id,
                payload={"host": host, "success": result.success, "message": result.message, "skill_count": len(set(skill_ids))},
            )

        status = "closed" if not failed_hosts else "partial_close"
        if status == "closed":
            self.db.set_leases_status([lease["lease_id"] for lease in active], "closed")
        else:
            to_close = [lease["lease_id"] for lease in active if lease["host"] not in failed_hosts]
            self.db.set_leases_status(to_close, "closed")

        deactivated_skills = len({(lease["host"], lease["skill_id"]) for lease in active if lease["host"] not in failed_hosts})
        self.db.add_audit_event(
            event_type="project.close",
            project_id=project_id,
            payload={"reason": reason, "deactivated": deactivated_skills, "status": status, "failed_hosts": failed_hosts},
        )

        return EndProjectResponse(project_id=project_id, deactivated_skills=deactivated_skills, status=status)

    def sweep_expired_leases(self) -> List[str]:
        now_iso = utc_now().isoformat()
        expired = self.db.get_expired_active_leases(now_iso=now_iso)
        if not expired:
            return []

        project_ids = sorted({lease["project_id"] for lease in expired})
        for project_id in project_ids:
            self.deactivate_project(project_id=project_id, reason="ttl_expiry")
            self.db.set_project_state(project_id, "closed", ended=True)

        return project_ids
