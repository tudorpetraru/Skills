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
