# Skill Autopilot

Local-first project skill orchestration for Claude/Codex desktop workflows.

## What it provides
1. Desktop UI with `Start Project`, `Status`, `End Project`, `History`.
2. Local API service on `127.0.0.1:8787`.
3. MCP server (`skill-autopilot-mcp`) for Claude/Codex integration.
4. Deterministic routing from `project_brief.md`.
5. Lease lifecycle and local SQLite audit history.
6. Action-plan execution via native `claude` / `codex` CLIs.
7. Optional distributed worker nodes.

## macOS install (recommended)
```bash
git clone https://github.com/tudorpetraru/Skills.git
cd Skills
./scripts/install_macos.sh
```

Optional: auto-write Claude MCP config during install.
```bash
./scripts/install_macos.sh --apply-claude-config
```

## Core commands
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-ui
~/.skill-autopilot/venv/bin/skill-autopilot-doctor
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --print-only
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --apply
```

## CLI commands and options
1. `skill-autopilot-ui` (no options)
2. `skill-autopilot-service [--host HOST] [--port PORT] [--config CONFIG] [--reload]`
3. `skill-autopilot-mcp [--config CONFIG] [--transport {stdio,sse,streamable-http}]`
4. `skill-autopilot-worker [--host HOST] [--port PORT] [--mode {native_cli,mock}] [--state-dir STATE_DIR]`
5. `skill-autopilot-doctor [--config CONFIG] [--json] [--strict]`
6. `skill-autopilot-configure-claude [--config-path CONFIG_PATH] [--server-name SERVER_NAME] [--transport {stdio,sse,streamable-http}] [--command COMMAND] [--print-only] [--apply]`
7. `./scripts/install_macos.sh [--python PYTHON] [--venv VENV_PATH] [--apply-claude-config]`
8. `./scripts/sync_skill_catalog.sh`
9. `python3 scripts/expand_skill_descriptions.py`

## MCP commands and options
1. `sa_start_project(workspace_path, brief_path?, host_targets?, auto_run=false, auto_approve_gates=true, wait_for_run_completion=false)`
2. `sa_project_status(project_id)`
3. `sa_reroute_project(project_id, force=false)`
4. `sa_end_project(project_id, reason=completed)`
5. `sa_project_history(limit=20)`
6. `sa_active_plan(project_id)`
7. `sa_service_health()`
8. `sa_run_project(project_id, auto_approve_gates=true, wait_for_completion=false)`
9. `sa_task_status(project_id, task_limit=50, include_outputs=false)`
10. `sa_approve_gate(project_id, gate_id, approved_by=human, note="")`
11. `sa_validate_brief_path(workspace_path="", brief_path?)`
12. `sa_job_status(job_id)`
13. `sa_jobs_recent(limit=20)`
14. `sa_observability_overview(stale_minutes=20, limit=25)`
15. `sa_project_observability(project_id, task_limit=20, audit_limit=20)`
16. `sa_reconcile_stale_projects(stale_minutes=20, close=false, close_reason=paused)`
17. `resource: skill-autopilot://policy`
18. `resource: skill-autopilot://observability`

## Full command/options reference
See: `docs/commands-reference.md`

Covered surfaces:
1. All installed CLI binaries and flags.
2. Installer and catalog scripts with options.
3. All MCP `sa_*` tools with arguments/defaults.
4. MCP resources and HTTP endpoints.
5. Task-to-model assignment rules (Claude vs Codex).

## Defaults
1. Config: `~/.project-skill-router/config.toml`
2. DB: `~/.project-skill-router/state.db`
3. Service URL: `http://127.0.0.1:8787`
4. Catalog preference: packaged `skill_autopilot/skills` library first, then optional local catalogs.
5. Curated catalog breadth: 115 skills across 18 categories (see `docs/skill-library.md`).

## Docs
1. macOS install guide: `docs/install-macos.md`
2. Claude MCP setup: `docs/claude-mcp-setup.md`
3. API contracts: `docs/api-contracts.md`
4. Commands reference: `docs/commands-reference.md`
5. Skill library map: `docs/skill-library.md`
6. Capability matrix: `docs/capability-matrix.md`

## Routing defaults
1. Excludes `.system*` skills.
2. Applies minimum relevance threshold.
3. Penalizes utility-only skills unless requested (`pdf`, `playwright`, `screenshot`).
4. Caps utility and per-cluster selection density.

## MCP execution model
1. `sa_start_project` returns project metadata immediately (does not auto-run by default).
2. `sa_run_project` is async by default and returns `job_id`.
3. Poll `sa_job_status` and `sa_task_status` for completion/results.
4. Use `sa_observability_overview` / `sa_project_observability` for live project monitoring in Claude.

## How tasks are assigned to Claude vs Codex
1. Each task gets an `agent_role` from decomposition or a phase default.
2. Default phase roles are `discovery -> orchestrator`, `build -> delivery`, `verify -> quality`, `ship -> orchestrator`.
3. `agent_role` is mapped to host using config `role_host_map`.
4. Default mapping is `orchestrator -> claude_desktop`, `research -> claude_desktop`, `quality -> codex_desktop`, `delivery -> codex_desktop`.
5. Worker pool dispatches to that host if available; if not, it falls back to round-robin across available hosts.
6. In `native_cli` mode, host execution is `claude_desktop -> claude -p ...` and `codex_desktop -> codex exec ...`.

## Tests
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

## Catalog maintenance
1. Source-of-truth catalog: `library/skills`.
2. Packaged runtime mirror: `skill_autopilot/skills`.
3. Regenerate rich job descriptions: `python3 scripts/expand_skill_descriptions.py`.
4. Sync command: `./scripts/sync_skill_catalog.sh`.
