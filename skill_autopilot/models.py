from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

HostTarget = Literal["claude_desktop", "codex_desktop"]


class ProjectState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


class EndReason(str, Enum):
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StartProjectRequest(BaseModel):
    workspace_path: str
    brief_path: str
    host_targets: List[HostTarget] = Field(default_factory=lambda: ["claude_desktop", "codex_desktop"])


class SkillReason(BaseModel):
    skill_id: str
    reason: str


class StartProjectResponse(BaseModel):
    project_id: str
    selected_skills: List[SkillReason]
    plan_id: str
    status: Literal["started"]


class GetProjectStatusResponse(BaseModel):
    project_id: str
    state: ProjectState
    active_hosts: List[HostTarget]
    active_skill_count: int
    last_route_at: Optional[datetime]


class EndProjectRequest(BaseModel):
    project_id: str
    reason: EndReason


class EndProjectResponse(BaseModel):
    project_id: str
    deactivated_skills: int
    status: Literal["closed", "partial_close", "error"]


class SkillLease(BaseModel):
    lease_id: str
    project_id: str
    skill_id: str
    host: HostTarget
    expires_at: datetime


class BriefIntent(BaseModel):
    goals: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    risk_tier: Literal["low", "medium", "high"] = "medium"
    evidence_level: Literal["standard", "strict"] = "standard"
    deliverables: List[str] = Field(default_factory=list)
    raw_text: str

    @field_validator("raw_text")
    @classmethod
    def validate_raw_text(cls, value: str) -> str:
        if len(value.strip()) < 40:
            raise ValueError("project_brief.md is too short to route reliably")
        return value


class SkillMetadata(BaseModel):
    skill_id: str
    name: str
    description: str
    tags: List[str] = Field(default_factory=list)
    hosts: List[HostTarget] = Field(default_factory=lambda: ["claude_desktop", "codex_desktop"])
    dependencies: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    source_repo: str
    pinned_ref: str


class RoutingPolicy(BaseModel):
    max_active_skills: int = 12
    max_context_tokens: int = 120_000
    risk_mode: Literal["low", "medium", "high"] = "medium"
    lease_ttl_hours: int = 24
    min_relevance_score: float = 0.22
    exclude_id_prefixes: List[str] = Field(default_factory=lambda: [".system"])
    utility_skill_ids: List[str] = Field(default_factory=lambda: ["pdf", "playwright", "screenshot"])
    utility_allow_terms: List[str] = Field(
        default_factory=lambda: ["pdf", "screenshot", "image", "browser", "scrape", "crawl", "playwright", "web"]
    )
    utility_penalty: float = 0.35
    max_utility_skills: int = 1
    max_skills_per_cluster: int = 4
    preferred_sources: List[str] = Field(default_factory=lambda: ["local_library"])
    preferred_source_bonus: float = 0.08


class RouteResult(BaseModel):
    route_id: str
    plan_hash: str
    selected_skills: List[SkillReason]
    rejected_skills: List[SkillReason] = Field(default_factory=list)
    snapshot_hash: str
    plan_payload: Dict[str, object]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    db_path: str
    service_time: datetime
    last_snapshot_hash: Optional[str] = None
    user_mode: Literal["standard", "admin"] = "standard"
    adapter_mode: str = "mock"
    worker_pool_size: int = 0
    remote_worker_count: int = 0


class HistoryEntry(BaseModel):
    project_id: str
    workspace_path: str
    state: ProjectState
    created_at: datetime
    updated_at: datetime
    selected_skill_count: int = 0


class AdapterResult(BaseModel):
    host: HostTarget
    success: bool
    message: str


class RunProjectRequest(BaseModel):
    project_id: str
    auto_approve_gates: bool = True


class RunProjectResponse(BaseModel):
    project_id: str
    run_id: str
    status: Literal["completed", "blocked", "failed"]
    executed_tasks: int
    pending_gates: List[str] = Field(default_factory=list)


class ApproveGateRequest(BaseModel):
    project_id: str
    gate_id: str
    approved_by: str = "human"
    note: str = ""


class ApproveGateResponse(BaseModel):
    project_id: str
    gate_id: str
    approved: bool
    approved_by: str


class TaskStatusResponse(BaseModel):
    project_id: str
    run_id: Optional[str] = None
    status: Optional[str] = None
    executed_tasks: int = 0
    tasks: List[Dict[str, object]] = Field(default_factory=list)
    approvals: List[Dict[str, object]] = Field(default_factory=list)
