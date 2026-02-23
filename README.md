# Skill Autopilot

Local-first project skill orchestration for Claude Desktop workflows.

## What it provides
1. Desktop UI with `Start Project`, `Status`, `End Project`, `History`.
2. Local API service on `127.0.0.1:8787`.
3. MCP server (`skill-autopilot-mcp`) for Claude Desktop integration.
4. Deterministic routing from `project_brief.md`.
5. Lease lifecycle and local SQLite audit history.
6. Pod architecture: Core pod (always-on) + attachable pods + B-kernels + industry mapping.
7. Task-by-task execution model: Claude Desktop works through plans via MCP tools.

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
4. `skill-autopilot-doctor [--config CONFIG] [--json] [--strict]`
5. `skill-autopilot-configure-claude [--config-path CONFIG_PATH] [--server-name SERVER_NAME] [--transport {stdio,sse,streamable-http}] [--command COMMAND] [--print-only] [--apply]`
6. `./scripts/install_macos.sh [--python PYTHON] [--venv VENV_PATH] [--apply-claude-config]`
7. `./scripts/sync_skill_catalog.sh`
8. `python3 scripts/expand_skill_descriptions.py`

## MCP tools

### Task workflow (primary)
1. `sa_start_project(workspace_path, brief_path?)` — parse brief, select pods/kernels, return first task.
2. `sa_next_task(project_id)` — get next pending task with instructions.
3. `sa_complete_task(project_id, task_id, summary?, artifacts?)` — mark done, return next task.
4. `sa_skip_task(project_id, task_id, reason?)` — skip task, return next.
5. `sa_approve_gate(project_id, gate_id, approved_by?, note?)` — unblock gated phases.

### Lifecycle
6. `sa_project_status(project_id)`
7. `sa_reroute_project(project_id, force?)`
8. `sa_end_project(project_id, reason?)`
9. `sa_project_history(limit?)`
10. `sa_active_plan(project_id)`

### Observability
11. `sa_service_health()`
12. `sa_task_status(project_id, task_limit?, include_outputs?)`
13. `sa_validate_brief_path(workspace_path?, brief_path?)`
14. `sa_observability_overview(stale_minutes?, limit?)`
15. `sa_project_observability(project_id, task_limit?, audit_limit?)`
16. `sa_reconcile_stale_projects(stale_minutes?, close?, close_reason?)`

### Resources
17. `resource: skill-autopilot://policy`
18. `resource: skill-autopilot://observability`

## Full command/options reference
See: `docs/commands-reference.md`

## Pod architecture
Every project gets the **Core pod** (always-on: orchestrator, scribe, research, quality, delivery tracker) plus automatically selected **attachable pods** and **B-kernels** based on industry detection and brief analysis.

- **7 attachable pods**: Discovery, Commercial, Finance & Governance, Legal/Risk, People & Talent, Ops & Supply, Data & Insight.
- **14 B-kernels**: Digital Product, Data & Analytics, ML/AI Systems, Cyber & SecOps, Embedded, Safety-Critical, Manufacturing, Chem/Materials, Life Sciences, Energy & Asset Ops, Financial Products, Construction, Content Production, Professional Services.
- **40-industry mapping**: brief text is auto-classified to an industry, which selects default kernel(s).

## MCP execution model
1. `sa_start_project` parses the brief, selects pods and kernels, generates a pod-aware plan, and returns the first task with full instructions.
2. Claude Desktop works through tasks by calling `sa_complete_task` or `sa_skip_task`.
3. `sa_next_task` returns the next pending task with pod context, acceptance criteria, and progress.
4. Phase gates auto-approve when all tasks in the gated phase are complete. Manual gate approval via `sa_approve_gate`.
5. When all tasks are complete, `sa_next_task` returns `status: "all_complete"`.
6. Call `sa_end_project` to close the project and deactivate leases.

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
