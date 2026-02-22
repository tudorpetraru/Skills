# macOS Troubleshooting

## `Server disconnected` in Claude MCP
1. Verify MCP runtime:
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-doctor
```
2. Verify Claude config entry:
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --print-only
```
3. Re-apply config and restart Claude:
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --apply
```

## `Brief file not found` but file exists
1. Use MCP diagnostic tool:
`sa_validate_brief_path`.
2. Confirm response fields:
`resolved_path`, `exists`, `is_file`, `readable`.
3. If `readable=false`, grant file access to Claude and restart.

## Permission error under `Documents`
Some macOS privacy settings block app sandboxes from reading certain paths.
Workarounds:
1. Grant Claude/Desktop Full Disk Access or Files and Folders permission.
2. Keep runtime under `~/.skill-autopilot` (default installer behavior).

## Python version issue
`skill-autopilot` requires Python 3.11+.
Check:
```bash
python3 --version
```
If needed, install 3.11+ and rerun:
```bash
./scripts/install_macos.sh --python /path/to/python3.11
```

## Optional CLIs missing
If doctor reports `claude` or `codex` missing:
1. Routing still works.
2. Native task execution for that host is unavailable until CLI is installed.
