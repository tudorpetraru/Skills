# Skill Autopilot API Contracts

Base URL: `http://127.0.0.1:8787`

This project also exposes equivalent MCP tools via `skill-autopilot-mcp`:

### Task workflow
1. `sa_start_project` — parse brief, select pods, return task list + deliverables for review
2. `sa_approve_plan` — approve the plan and start execution, returns first task
3. `sa_next_task` — get next pending task
4. `sa_complete_task` — mark done, return next
5. `sa_skip_task` — skip, return next
6. `sa_approve_gate` — unblock gated phases

### Lifecycle
6. `sa_project_status`
7. `sa_reroute_project` (`force` optional)
8. `sa_end_project`
9. `sa_project_history`
10. `sa_active_plan`
11. `sa_service_health`
12. `sa_task_status` (`task_limit`, `include_outputs` optional)
13. `sa_validate_brief_path`

### Observability
14. `sa_observability_overview`
15. `sa_project_observability`
16. `sa_reconcile_stale_projects`

## MCP Execution Model
1. `sa_start_project` parses the brief, selects pods/kernels, generates a plan, and returns the task list + deliverables for user review. Status is `pending_approval`.
2. The user reviews the plan. Once approved, call `sa_approve_plan` to start execution and get the first task.
3. Claude Desktop works through tasks by calling `sa_complete_task` or `sa_skip_task`.
4. `sa_next_task` returns the next pending task with instructions, acceptance criteria, and a `task_list` checklist.
5. Phase gates auto-approve when all tasks in the gated phase complete. Use `sa_approve_gate` for manual overrides.
6. When all tasks are done, `sa_next_task` returns `status: "all_complete"`.

## MCP Observability (Claude-side monitoring)
1. `sa_observability_overview` gives a DB-only live view of active projects with `classification=progressing|stale`.
2. `sa_project_observability` drills into one project (latest run, recent tasks, approvals, audit events, leases).
3. `sa_reconcile_stale_projects` can optionally close stale projects (`close=true`) with a safe reason (`paused` default).
4. Resource `skill-autopilot://observability` exposes a lightweight table for quick in-app visibility.

## POST /start-project
Starts a project from a workspace brief.

Request:
```json
{
  "workspace_path": "string",
  "brief_path": "string",
  "host_targets": ["claude_desktop"]
}
```

Response:
```json
{
  "project_id": "string",
  "status": "pending_approval",
  "plan_id": "string",
  "task_list": "# Plan Overview: 12 tasks\n...",
  "deliverables": ["REST API spec", "Database schema", "..."]
}
```

## GET /project-status/{project_id}
Returns current lifecycle status and active host footprint.

Response:
```json
{
  "project_id": "string",
  "state": "idle|active|closing|closed|error",
  "active_hosts": ["claude_desktop"],
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
  "host": "claude_desktop",
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
