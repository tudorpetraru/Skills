# Claude MCP Setup

## 1) Install runtime
Use the repo installer:
```bash
./scripts/install_macos.sh
```

Or install manually in your preferred venv:
```bash
python3 -m venv ~/.skill-autopilot/venv
source ~/.skill-autopilot/venv/bin/activate
pip install /path/to/Skills
```

## 2) Configure Claude
Recommended:
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --apply
```

Preview JSON snippet only:
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --print-only
```

Manual config location:
`~/Library/Application Support/Claude/claude_desktop_config.json`

## 3) Restart Claude Desktop
After restart, Claude should list these MCP tools:
1. `sa_start_project`
2. `sa_project_status`
3. `sa_reroute_project`
4. `sa_end_project`
5. `sa_project_history`
6. `sa_active_plan`
7. `sa_service_health`
8. `sa_run_project`
9. `sa_task_status`
10. `sa_approve_gate`
11. `sa_validate_brief_path`

## 4) Example usage in Claude
1. Call `sa_start_project` with `workspace_path` and optional `brief_path` (it auto-runs execution by default).
2. Call `sa_task_status` to inspect task-level execution results.
3. If blocked on a gate, call `sa_approve_gate`, then `sa_run_project`.
4. Call `sa_end_project` when done.
5. If a brief path fails, call `sa_validate_brief_path` first to see resolved path and read/permission diagnostics.

## Notes
- Skill routing now excludes `.system*` skills by default.
- Utility skills (`pdf`, `playwright`, `screenshot`) are penalized and capped unless explicitly requested in the brief.
- Local policy is available as resource `skill-autopilot://policy`.
