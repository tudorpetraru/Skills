# Skill Autopilot Architecture

## High-Level Components
1. Desktop Shell App (Tkinter):
  1. Buttons: `Start Project`, `Status`, `End Project`, `History`.
  2. Starts local router service automatically.
  3. Presents concise lifecycle summaries.
2. Router Service (FastAPI + core modules):
  1. Brief parsing and validation.
  2. Catalog loading and snapshot hashing.
  3. Deterministic scoring/composition.
  4. Lease lifecycle management.
  5. Pod-aware decomposition plan generation.
  6. Audit event persistence.
3. Pod System:
  1. Core pod (always-on): orchestrator, scribe, research, quality, delivery tracker.
  2. 7 attachable pods: Discovery, Commercial, Finance, Legal, People, Ops, Data.
  3. 14 B-kernel families for domain-specific delivery.
  4. 40-industry mapping for automatic kernel selection.
4. MCP Integration Server:
  1. `skill-autopilot-mcp` tool server over stdio/SSE/streamable-http.
  2. Task-by-task execution model: Claude Desktop is the primary agent.
  3. `sa_next_task` / `sa_complete_task` / `sa_skip_task` for plan execution.
5. Task State Machine (executor):
  1. Tasks flow: pending → active → completed / skipped / failed.
  2. Phase gates auto-approve when all tasks in gated phase complete.
  3. Tracks progress and run state in SQLite.
6. State Store (SQLite):
  1. Projects.
  2. Routes.
  3. Leases.
  4. Audit events.
  5. Generated plans.
  6. Project runs and task runs.
  7. Gate approvals.
7. File Watcher:
  1. Watches active `project_brief.md` files.
  2. Triggers reroute on material changes.
8. TTL Sweeper:
  1. Periodically closes expired leases.
  2. Serves as safety fallback if project is not manually ended.

## Runtime Sequence
1. User calls `sa_start_project` (via Claude Desktop or UI).
2. Service validates brief and normalizes intent.
3. Brief parser detects industry, project type, and pod hints.
4. Catalog manager builds skill snapshot from allowlisted sources.
5. Router scores and composes compatible skill set.
6. Pod selector attaches Core pod + relevant attachable pods + B-kernel(s).
7. Decomposer builds pod-aware action plan with per-task instructions.
8. Lease manager activates selected skills on Claude Desktop host.
9. Task state machine starts run and returns first task.
10. Claude Desktop works through tasks via `sa_complete_task` / `sa_next_task`.
11. Phase gates auto-approve or block as configured.
12. Watcher monitors brief for material changes and reroutes when needed.
13. User calls `sa_end_project` when done, leases are deactivated and project is closed.

## Execution Model
1. MCP server is a **planner and tracker**, not an executor.
2. Claude Desktop is the primary agent that works through the plan.
3. Each task includes: pod context, agent role, skill instructions, acceptance criteria, inputs, outputs, guardrails.
4. All roles map to `claude_desktop` host.
5. Tasks are tracked in SQLite: pending → active → completed/skipped/failed.

## Data Model
- `projects`: lifecycle state and workspace metadata.
- `routes`: route hash, selected/rejected skills, brief hash.
- `plans`: generated action plans (with pods, kernels, phases, tasks).
- `leases`: per-skill activations with expiry.
- `audit_events`: append-only lifecycle and policy events.
- `project_runs`: execution runs (status, summary, timestamps).
- `task_runs`: per-task execution records (status/output/error).
- `gate_approvals`: gate approval state for blocked phases.

## Determinism Strategy
1. Canonical JSON serialization with sorted keys.
2. Stable sorting on score desc, then skill_id asc.
3. Plan hash based on normalized intent + selected skill IDs + snapshot hash.
4. Snapshot hash based on canonical catalog metadata.

## Security and Policy
1. Catalog sources must be allowlisted.
2. Catalog metadata includes pinned refs for source immutability.
3. Skill count and token-budget caps enforced in routing policy.
4. Admin mode gate for policy and catalog changes.
5. Internal/system skills are excluded by default (`.system*` prefix policy).
6. Utility skills are penalized/capped unless explicitly requested in brief text.

## Known Prototype Constraints
1. UI is intentionally minimal and local-only.
2. Installer packaging is documented but not bundled as a signed installer.
