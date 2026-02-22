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
4. Skill library map: `docs/skill-library.md`
5. Capability matrix: `docs/capability-matrix.md`

## Routing defaults
1. Excludes `.system*` skills.
2. Applies minimum relevance threshold.
3. Penalizes utility-only skills unless requested (`pdf`, `playwright`, `screenshot`).
4. Caps utility and per-cluster selection density.

## MCP execution model
1. `sa_start_project` returns project metadata immediately (does not auto-run by default).
2. `sa_run_project` is async by default and returns `job_id`.
3. Poll `sa_job_status` and `sa_task_status` for completion/results.

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
3. Sync command: `./scripts/sync_skill_catalog.sh`.
