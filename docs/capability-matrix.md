# Capability Matrix (Current Build)

## Fully Available
1. Brief parsing and routing from `project_brief.md`.
2. Skill activation/deactivation lifecycle with leases.
3. Curated local skill library selection with dependency/conflict checks.
4. Action-plan generation by phase.
5. Orchestrator execution runtime (`run-project`) with per-task persistence.
6. Gate approval workflow (`approve-gate`) and blocked-run handling.
7. MCP integration with namespaced tools (`sa_*`).
8. SQLite audit trail for routing and execution.

## Available With Current Limitations
1. Host adapters are local mock adapters (file-backed activation footprints).
2. Task execution is deterministic role-runtime execution, not remote execution inside Claude/Codex internals.
3. Gate mapping is currently defaulted (`gate-1` after discovery, `gate-2` after verify).

## Not Implemented Yet
1. Native Claude/Codex host SDK adapter for in-agent skill enforcement/telemetry.
2. Distributed worker execution across separate agent processes.
3. Multi-user auth, tenancy, and remote orchestration.

## Source of Truth
- API: `/Users/tudor/Documents/AI/Skills/docs/api-contracts.md`
- MCP setup: `/Users/tudor/Documents/AI/Skills/docs/claude-mcp-setup.md`
- Skill catalog: `/Users/tudor/Documents/AI/Skills/docs/skill-library.md`
