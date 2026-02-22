# Skill Autopilot API Contracts

Base URL: `http://127.0.0.1:8787`

This project also exposes equivalent MCP tools via `skill-autopilot-mcp`:
1. `sa_start_project`
2. `sa_project_status`
3. `sa_reroute_project`
4. `sa_end_project`
5. `sa_project_history`
6. `sa_active_plan`
7. `sa_service_health`
8. `sa_run_project`
9. `sa_task_status`
10. `sa_approve_gate`
11. `sa_validate_brief_path`
12. `sa_job_status`
13. `sa_jobs_recent`
14. `sa_observability_overview`
15. `sa_project_observability`
16. `sa_reconcile_stale_projects`

## MCP Async Behavior (important)
1. `sa_start_project` defaults to `auto_run=false`, so it returns quickly with `project_id`.
2. If `sa_start_project` is called with `auto_run=true`, execution is dispatched async by default and returns `execution.job_id`.
3. `sa_run_project` dispatches async by default and returns:
```json
{
  "status": "accepted",
  "job_id": "string",
  "project_id": "string"
}
```
4. Poll `sa_job_status(job_id)` for completion and final run result payload.
5. Set `wait_for_completion=true` only when you explicitly want blocking behavior.

## MCP Observability (Claude-side monitoring)
1. `sa_observability_overview` gives a DB-only live view of active projects with `classification=progressing|stale`.
2. `sa_project_observability` drills into one project (latest run, recent tasks, approvals, audit events, leases).
3. `sa_reconcile_stale_projects` can optionally close stale projects (`close=true`) with a safe reason (`paused` default).
4. Resource `skill-autopilot://observability` exposes a lightweight table for quick in-app visibility.

## POST /start-project
Starts or reactivates a project from a workspace brief.

Request:
```json
{
  "workspace_path": "string",
  "brief_path": "string",
  "host_targets": ["claude_desktop", "codex_desktop"]
}
```

Response:
```json
{
  "project_id": "string",
  "selected_skills": [{"skill_id":"string", "reason":"string"}],
  "plan_id": "string",
  "status": "started"
}
```

## GET /project-status/{project_id}
Returns current lifecycle status and active host footprint.

Response:
```json
{
  "project_id": "string",
  "state": "idle|active|closing|closed|error",
  "active_hosts": ["claude_desktop", "codex_desktop"],
  "active_skill_count": 0,
  "last_route_at": "RFC3339"
}
```

## POST /end-project
Closes project and deactivates all active leases.

Request:
```json
{
  "project_id": "string",
  "reason": "completed|paused|cancelled"
}
```

Response:
```json
{
  "project_id": "string",
  "deactivated_skills": 0,
  "status": "closed|partial_close|error"
}
```

## GET /history
Returns recent projects and route summaries.

## GET /health
Returns service health, DB state, and last catalog snapshot metadata.

## POST /run-project
Executes the latest project action plan via orchestrator runtime.

Request:
```json
{
  "project_id": "string",
  "auto_approve_gates": true
}
```

Response:
```json
{
  "project_id": "string",
  "run_id": "string",
  "status": "completed|blocked|failed",
  "executed_tasks": 0,
  "pending_gates": ["gate-1"]
}
```

## GET /task-status/{project_id}
Returns latest run status and per-task outputs.

## POST /approve-gate
Approves a blocked execution gate.

Request:
```json
{
  "project_id": "string",
  "gate_id": "gate-1",
  "approved_by": "human",
  "note": "Approved to continue"
}
```

## Internal Logical Types
### SkillLease
```json
{
  "lease_id": "string",
  "project_id": "string",
  "skill_id": "string",
  "host": "claude_desktop|codex_desktop",
  "expires_at": "RFC3339"
}
```

### Route Output (internal)
```json
{
  "route_id": "string",
  "plan_hash": "sha256",
  "selected_skills": ["skill_id"],
  "rejected_skills": [{"skill_id":"string", "reason":"string"}],
  "catalog_snapshot_hash": "sha256"
}
```
