# Commands and Options Reference

This is the complete command surface for the current build.

## Installed CLI Commands

### `skill-autopilot-ui`
Launches the desktop app.

Usage:
```bash
skill-autopilot-ui
```

Options:
1. None.

### `skill-autopilot-service`
Runs the local FastAPI service.

Usage:
```bash
skill-autopilot-service [--host HOST] [--port PORT] [--config CONFIG] [--reload]
```

Options:
1. `--host HOST`: Bind host (default from config, usually `127.0.0.1`).
2. `--port PORT`: Bind port (default from config, usually `8787`).
3. `--config CONFIG`: Path to config TOML.
4. `--reload`: Enable uvicorn auto-reload (dev only).

### `skill-autopilot-mcp`
Runs the MCP server for Claude Desktop.

Usage:
```bash
skill-autopilot-mcp [--config CONFIG] [--transport {stdio,sse,streamable-http}]
```

Options:
1. `--config CONFIG`: Path to config TOML.
2. `--transport`: MCP transport (`stdio` default).

### `skill-autopilot-doctor`
Runs installation/runtime checks.

Usage:
```bash
skill-autopilot-doctor [--config CONFIG] [--json] [--strict]
```

Options:
1. `--config CONFIG`: Path to config TOML.
2. `--json`: Emit machine-readable JSON.
3. `--strict`: Fail on optional check failures too.

### `skill-autopilot-configure-claude`
Creates/updates Claude Desktop MCP config.

Usage:
```bash
skill-autopilot-configure-claude [--config-path CONFIG_PATH] [--server-name SERVER_NAME] [--transport {stdio,sse,streamable-http}] [--command COMMAND] [--print-only] [--apply]
```

Options:
1. `--config-path CONFIG_PATH`: Claude config path (default: `~/Library/Application Support/Claude/claude_desktop_config.json`).
2. `--server-name SERVER_NAME`: MCP server key (default `skill-autopilot`).
3. `--transport`: `stdio` (default), `sse`, or `streamable-http`.
4. `--command COMMAND`: Override MCP executable path.
5. `--print-only`: Print snippet only; do not write file.
6. `--apply`: Write into Claude config file.

## Repo Scripts

### `./scripts/install_macos.sh`
Bootstraps local runtime venv, installs package, runs doctor.

Usage:
```bash
./scripts/install_macos.sh [--python PYTHON] [--venv VENV_PATH] [--apply-claude-config]
```

Options:
1. `--python PYTHON`: Python binary to try first (must be 3.11+).
2. `--venv VENV_PATH`: Install venv location (default `~/.skill-autopilot/venv`).
3. `--apply-claude-config`: Also run `skill-autopilot-configure-claude --apply`.

### `./scripts/sync_skill_catalog.sh`
Syncs `library/skills` into packaged runtime catalog `skill_autopilot/skills`.

Usage:
```bash
./scripts/sync_skill_catalog.sh
```

Options:
1. None.

### `python3 scripts/expand_skill_descriptions.py`
Expands/rewrites skill job descriptions across catalog files.

Usage:
```bash
python3 scripts/expand_skill_descriptions.py
```

Options:
1. None.

## MCP Tools and Arguments

All tool names are namespaced with `sa_`.

### Task Workflow (primary flow)

#### `sa_start_project`
Parses the brief, selects pods and B-kernels, generates a pod-aware plan, and returns the first task.

Arguments:
1. `workspace_path` (required): project directory path.
2. `brief_path` (optional): brief file path. Default: `<workspace_path>/project_brief.md`.

#### `sa_next_task`
Returns the next pending task with full instructions, pod context, acceptance criteria, and progress.

Arguments:
1. `project_id` (required).

Returns:
- `status: "ready"` with `task` object when a task is available.
- `status: "blocked"` with `blocked_by_gate` when a gate needs approval.
- `status: "all_complete"` when all tasks are done.

#### `sa_complete_task`
Marks a task as completed and returns the next task.

Arguments:
1. `project_id` (required).
2. `task_id` (required).
3. `summary` (optional): completion summary.
4. `artifacts` (optional): list of artifact paths produced.

#### `sa_skip_task`
Skips a task with a reason and returns the next task.

Arguments:
1. `project_id` (required).
2. `task_id` (required).
3. `reason` (optional): why the task was skipped.

### Lifecycle

#### `sa_project_status`
Arguments:
1. `project_id` (required).

#### `sa_reroute_project`
Arguments:
1. `project_id` (required).
2. `force` (optional, default `false`): force reroute even when diff is not material.

#### `sa_end_project`
Arguments:
1. `project_id` (required).
2. `reason` (optional, default `completed`): `completed|paused|cancelled`.

#### `sa_project_history`
Arguments:
1. `limit` (optional, default `20`, capped at `100`).

#### `sa_active_plan`
Arguments:
1. `project_id` (required).

#### `sa_service_health`
Arguments:
1. None.

#### `sa_task_status`
Arguments:
1. `project_id` (required).
2. `task_limit` (optional, default `50`, max `500`).
3. `include_outputs` (optional, default `false`).

#### `sa_approve_gate`
Arguments:
1. `project_id` (required).
2. `gate_id` (required).
3. `approved_by` (optional, default `human`).
4. `note` (optional, default empty string).

#### `sa_validate_brief_path`
Arguments:
1. `workspace_path` (optional, default empty string).
2. `brief_path` (optional).

### Observability

#### `sa_observability_overview`
Arguments:
1. `stale_minutes` (optional, default `20`).
2. `limit` (optional, default `25`).

#### `sa_project_observability`
Arguments:
1. `project_id` (required).
2. `task_limit` (optional, default `20`).
3. `audit_limit` (optional, default `20`).

#### `sa_reconcile_stale_projects`
Arguments:
1. `stale_minutes` (optional, default `20`).
2. `close` (optional, default `false`).
3. `close_reason` (optional, default `paused`).

## MCP Resources
1. `skill-autopilot://policy`: effective routing policy values.
2. `skill-autopilot://observability`: live table summary of active projects.

## HTTP API Endpoints
Base URL default: `http://127.0.0.1:8787`

1. `POST /start-project`
2. `GET /project-status/{project_id}`
3. `POST /end-project`
4. `GET /task-status/{project_id}`
5. `POST /approve-gate`
6. `GET /history`
7. `GET /health`

Detailed request/response contracts: `docs/api-contracts.md`.

## Config Example
```toml
[policy]
role_host_map = "orchestrator:claude_desktop,research:claude_desktop,quality:claude_desktop,delivery:claude_desktop"
adapter_mode = "claude_desktop"
worker_pool_size = 1
default_industry = ""
```
