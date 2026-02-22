# Skill Autopilot (Prototype)

A local-first desktop prototype that automatically routes project skills for Claude/Codex-style desktop workflows.

## What it provides
1. Minimal desktop UI: `Start Project`, `Status`, `End Project`, `History`.
2. Background API service on `127.0.0.1:8787`.
3. Deterministic routing from `project_brief.md`.
4. Lease-based activation/deactivation for `claude_desktop` and `codex_desktop` adapters.
5. SQLite-backed lifecycle and audit history.
6. Auto reroute on material brief changes.
7. MCP server for Claude/Codex integration (`skill-autopilot-mcp`).

## Quick start
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install .
skill-autopilot-ui
```

The UI launches and starts the local service automatically.

## Defaults
- Config path: `~/.project-skill-router/config.toml`
- Database path: `~/.project-skill-router/state.db`
- Service URL: `http://127.0.0.1:8787`

If no config exists, the app creates a safe default with allowlisted local catalog roots.

## API
See `docs/api-contracts.md`.

## Claude MCP
1. Install with Python 3.11+.
2. Point Claude desktop to `skill-autopilot-mcp --transport stdio`.
3. Use MCP tools: `sa_start_project`, `sa_run_project`, `sa_task_status`, `sa_approve_gate`, `sa_end_project`.

See `docs/claude-mcp-setup.md` for exact config.

## Routing quality defaults
1. Excludes internal `.system*` skills by policy.
2. Uses relevance threshold before selecting a skill.
3. Penalizes utility-only skills unless explicitly requested in brief text.
4. Caps utility skill count and cluster density to reduce noisy selections.
5. Prefers the local curated source: `/Users/tudor/Documents/AI/Skills/library/skills`.

## Curated skill library
1. Real catalog lives at `/Users/tudor/Documents/AI/Skills/library/skills`.
2. Category map is documented in `/Users/tudor/Documents/AI/Skills/docs/skill-library.md`.

## Capability Clarity
1. Current capability matrix (fully available vs limited vs not implemented) is documented at:
`/Users/tudor/Documents/AI/Skills/docs/capability-matrix.md`.

## Tests
```bash
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

## Note on host adapters
This prototype includes local adapter stubs that model activation/deactivation behavior and capability reporting. They can be replaced with real desktop host integrations without changing routing contracts.
