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
9. Native CLI execution adapters for Claude and Codex hosts.
10. Distributed worker pool with role-based host routing.
11. Optional remote worker endpoints and standalone worker node service.

## Available With Current Limitations
1. Native execution uses official host CLIs (`claude`, `codex`) rather than private desktop SDK hooks.
2. Gate mapping is currently defaulted (`gate-1` after discovery, `gate-2` after verify).
3. Full-project runs can be expensive for large plans because each task is an LLM call.

## Not Implemented Yet
1. Native desktop SDK adapter for in-app internal telemetry (if vendors expose stable SDK APIs).
2. Multi-user auth, tenancy, and remote orchestration control plane.

## Source of Truth
- API: `/Users/tudor/Documents/AI/Skills/docs/api-contracts.md`
- MCP setup: `/Users/tudor/Documents/AI/Skills/docs/claude-mcp-setup.md`
- Skill catalog: `/Users/tudor/Documents/AI/Skills/docs/skill-library.md`
