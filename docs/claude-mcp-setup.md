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

### Task workflow
1. `sa_start_project`
2. `sa_approve_plan`
3. `sa_next_task`
4. `sa_complete_task`
5. `sa_skip_task`

### Lifecycle
5. `sa_project_status`
6. `sa_reroute_project`
7. `sa_end_project`
8. `sa_project_history`
9. `sa_active_plan`
10. `sa_approve_gate`

### Observability
11. `sa_service_health`
12. `sa_task_status`
13. `sa_validate_brief_path`
14. `sa_observability_overview`
15. `sa_project_observability`
16. `sa_reconcile_stale_projects`

## 4) Example usage in Claude
1. Call `sa_start_project` with `workspace_path`. Returns the task list and deliverables for review (execution does NOT start yet).
2. Present the task list and deliverables to the user for approval.
3. Once approved, call `sa_approve_plan` with `project_id` to start execution and get the first task.
4. Work on the task following the instructions, acceptance criteria, and guardrails.
5. Call `sa_complete_task` with `project_id`, `task_id`, and a `summary` of what you did.
6. The response includes the `next` task. Work through it the same way.
7. If `sa_next_task` returns `status: "blocked"`, call `sa_approve_gate` to unblock the phase.
8. Continue until `sa_next_task` returns `status: "all_complete"`.
9. Call `sa_end_project` when done.
10. If a brief path fails, call `sa_validate_brief_path` for resolution diagnostics.
11. Use `sa_observability_overview` to monitor live projects and detect stale runs.

## Notes
- For LLM-powered industry detection, install the optional `anthropic` dependency (`pip install -e '.[llm]'`) and add `ANTHROPIC_API_KEY` to the MCP server env in `claude_desktop_config.json`:
  ```json
  "env": { "ANTHROPIC_API_KEY": "sk-ant-..." }
  ```
- Skill routing excludes `.system*` skills by default.
- Utility skills (`pdf`, `playwright`, `screenshot`) are penalized and capped unless explicitly requested in the brief.
- Local policy is available as resource `skill-autopilot://policy`.
- For VM/host path differences, set `SKILL_AUTOPILOT_PATH_MAPS` in MCP env if needed.
- Full CLI/MCP options reference: `docs/commands-reference.md`.
