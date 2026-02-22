# Claude MCP Setup

This project includes a real MCP server entrypoint:

- Command: `skill-autopilot-mcp`
- Module: `skill_autopilot.mcp_server`
- Default transport: `stdio` (recommended for Claude desktop)

## 1) Install and verify
```bash
cd /Users/tudor/Documents/AI/Skills
mkdir -p /Users/tudor/.skill-autopilot
/opt/homebrew/bin/python3.11 -m venv /Users/tudor/.skill-autopilot/venv
source /Users/tudor/.skill-autopilot/venv/bin/activate
pip install /Users/tudor/Documents/AI/Skills
/Users/tudor/.skill-autopilot/venv/bin/skill-autopilot-mcp --help
```

## 2) Add to Claude desktop MCP config
Create or edit Claude desktop config and add this server entry:

```json
{
  "mcpServers": {
    "skill-autopilot": {
      "command": "/Users/tudor/.skill-autopilot/venv/bin/skill-autopilot-mcp",
      "args": ["--transport", "stdio"],
      "env": {}
    }
  }
}
```

This path avoids macOS permission issues that can occur when Claude launches a venv binary under `Documents`.

## 3) Restart Claude desktop
After restart, Claude can call these MCP tools:
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

## 4) Example usage inside Claude
1. Call `sa_start_project` with `workspace_path` and optional `brief_path` (it auto-runs execution by default).
2. Call `sa_task_status` to inspect task-level execution results.
3. If blocked on a gate, call `sa_approve_gate`, then `sa_run_project`.
4. Call `sa_end_project` when done.

## Notes
- Skill routing now excludes `.system*` skills by default.
- Utility skills (`pdf`, `playwright`, `screenshot`) are penalized and capped unless explicitly requested in the brief.
- Local policy is available as resource `skill-autopilot://policy`.
