# Skill Autopilot Requirements

## Product Intent
Skill Autopilot is a single desktop application for non-technical users that manages project-scoped skills for Claude and Codex automatically.

Primary UX:
1. Put `project_brief.md` in a workspace.
2. Click `Start Project`.
3. Work in Claude/Codex.
4. Click `End Project`.

## Goals
1. Zero terminal/config work for standard users.
2. Deterministic skill routing for repeatable outcomes.
3. Safe lifecycle management (no orphan active skills).
4. Local-first operation with auditable state.

## Functional Requirements
1. Detect and validate `project_brief.md` before project start.
2. Route skills from curated catalogs and activate on selected hosts.
3. Exclude internal/system skills by default policy (e.g. `.system*`).
4. Penalize and cap utility-only skills unless explicitly requested.
5. Show selected skills and selection reasons.
6. Produce a phase-based action plan.
7. Execute tasks through orchestrator runtime with task-level state persistence.
8. Support gate approvals to continue blocked runs.
9. Re-route when the brief changes materially during active projects.
10. Deactivate all project skills on `End Project`.
11. Persist project state, routes, leases, runs, task outputs, and audit events locally.
12. Expose lifecycle and execution operations through MCP for Claude integration.
13. Support distributed workers (local + optional remote endpoints).
14. Support user modes:
1. Standard mode: no policy/catalog editing.
2. Admin mode: policy and catalog management enabled.

## Non-Functional Requirements
1. Time to first successful setup under 3 minutes.
2. Start-project latency under 10 seconds on typical catalog size.
3. Deterministic route output for same brief + same catalog snapshot.
4. Crash-safe restart and lease recovery.
5. Offline-safe fallback to last known catalog snapshot.

## Security Requirements
1. Catalog sources are allowlisted by default.
2. Catalog revisions are pinned and snapshot hashed.
3. Least-privilege tool policy profile by default.
4. All lifecycle operations are audit logged.

## Acceptance Criteria
1. Non-technical user can complete start->work->end lifecycle in UI only.
2. Zero orphan leases within 5 minutes after project close in normal operation.
3. Valid brief starts successfully and returns skill reasons + plan.
4. Invalid brief fails with clear validation message.
5. Reroute applies only changed skill set (add/remove/retain semantics).
