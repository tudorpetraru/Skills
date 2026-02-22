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
5. Decomposition plan generation.
6. Audit event persistence.
3. Host Adapters:
1. `claude_desktop` adapter.
2. `codex_desktop` adapter.
3. Local mock activation/deactivation hooks for phase-1 prototype.
4. MCP Integration Server:
1. `skill-autopilot-mcp` tool server over stdio/SSE/streamable-http.
2. Exposes project lifecycle tools for Claude/Codex MCP clients.
4. State Store (SQLite):
1. Projects.
2. Routes.
3. Leases.
4. Audit events.
5. Generated plans.
5. File Watcher:
1. Watches active `project_brief.md` files.
2. Triggers reroute on material changes.
6. TTL Sweeper:
1. Periodically closes expired leases.
2. Serves as safety fallback if project is not manually ended.

## Runtime Sequence
1. User clicks `Start Project`.
2. Service validates brief and normalizes intent.
3. Catalog manager builds skill snapshot from allowlisted sources.
4. Router scores and composes compatible skill set.
5. Lease manager activates selected skills on target hosts.
6. Decomposer builds phase-oriented action plan.
7. State and audit events are persisted.
8. Watcher monitors brief for material changes and reroutes when needed.
9. User clicks `End Project`, leases are deactivated and project is closed.

## Data Model
- `projects`: lifecycle state and workspace metadata.
- `routes`: route hash, selected/rejected skills, brief hash.
- `plans`: generated action plans.
- `leases`: per-skill per-host activations with expiry.
- `audit_events`: append-only lifecycle and policy events.

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
1. Desktop host adapters are local mock integrations in this version.
2. Installer packaging is documented but not bundled as a signed installer.
3. UI is intentionally minimal and local-only.
