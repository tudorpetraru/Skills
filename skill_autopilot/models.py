from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

HostTarget = Literal["claude_desktop"]


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


class TaskState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class StartProjectRequest(BaseModel):
    workspace_path: str
    brief_path: str
    host_targets: List[HostTarget] = Field(default_factory=lambda: ["claude_desktop"])


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
    industry: str = ""
    project_type: str = ""
    pod_hints: List[str] = Field(default_factory=list)
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
    hosts: List[HostTarget] = Field(default_factory=lambda: ["claude_desktop"])
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
    adapter_mode: str = "claude_desktop"
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
    total_tasks: int = 0
    summary: Dict[str, object] = Field(default_factory=dict)
    tasks: List[Dict[str, object]] = Field(default_factory=list)
    approvals: List[Dict[str, object]] = Field(default_factory=list)


# --- Pod and task instruction models ---


class PodAssignment(BaseModel):
    """A pod attached to a project with its selected agents."""
    pod_id: str
    pod_name: str
    agents: List[str] = Field(default_factory=list)
    kernel_id: Optional[str] = None
    always_on: bool = False


class TaskInstruction(BaseModel):
    """A single task with full context for Claude Desktop to execute."""
    task_id: str
    title: str
    phase: str
    state: TaskState = TaskState.PENDING
    pod_id: str = ""
    agent: str = ""
    skill_id: str = ""
    instructions: str = ""
    acceptance_criteria: List[str] = Field(default_factory=list)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    guardrails: List[str] = Field(default_factory=list)
    order_index: int = 0


class CompleteTaskRequest(BaseModel):
    project_id: str
    task_id: str
    summary: str = ""
    artifacts: List[str] = Field(default_factory=list)
    evidence: Dict[str, object] = Field(default_factory=dict)


class SkipTaskRequest(BaseModel):
    project_id: str
    task_id: str
    reason: str = ""
