# Changelog

## 2026-02-23 — Claude Desktop Optimization + Pod Architecture

### Breaking Changes
- **Removed `sa_run_project` MCP tool** — replaced by task-by-task execution model.
- **Removed `sa_job_status` and `sa_jobs_recent`** — async job system no longer needed.
- **Dropped `codex_desktop`** from `HostTarget` — all execution is Claude Desktop only.
- **`sa_start_project` signature simplified** — removed `auto_run`, `auto_approve_gates`, `wait_for_run_completion`, `host_targets` parameters.

### New MCP Tools
- `sa_next_task(project_id)` — returns next pending task with full instructions, pod context, and progress.
- `sa_complete_task(project_id, task_id, summary?, artifacts?)` — marks task done, returns next task.
- `sa_skip_task(project_id, task_id, reason?)` — skips task, returns next task.

### New Execution Model
- MCP server is now a **planner + tracker**, not an executor.
- Claude Desktop works through plans task-by-task via `sa_next_task` / `sa_complete_task`.
- Phase gates auto-approve when all tasks in the gated phase are complete.
- `sa_start_project` auto-starts a run and returns the first task inline.

### Pod Architecture (restored from project brief)
- **Core pod** (always-on): orchestrator, scribe, research, quality, delivery tracker.
- **7 attachable pods**: Discovery, Commercial, Finance & Governance, Legal/Risk, People & Talent, Ops & Supply, Data & Insight.
- **14 B-kernel families**: Digital Product, Data & Analytics, ML/AI Systems, Cyber & SecOps, Embedded, Safety-Critical, Manufacturing, Chem/Materials, Life Sciences, Energy & Asset Ops, Financial Products, Construction, Content Production, Professional Services.
- **40-industry mapping**: auto-detects industry from brief text → selects default kernel(s).
- **Pod-aware task generation**: each task carries pod_id, agent, skill_id, instructions, acceptance criteria, inputs, outputs, and guardrails.

### Files Changed
- `models.py` — dropped codex_desktop, added TaskState, TaskInstruction, PodAssignment, industry fields.
- `pods.py` — **NEW** — Core pod, 7 attachable pods, 14 B-kernels, 40-industry map, selection logic.
- `brief_parser.py` — detects industry, project type, pod hints from brief text.
- `decomposer.py` — pod-aware task generation across 4 phases.
- `executor.py` — replaced OrchestratorExecutor with TaskStateMachine (next/complete/skip).
- `mcp_server.py` — added sa_next_task, sa_complete_task, sa_skip_task; removed sa_run_project.
- `engine.py` — Claude Desktop only, uses TaskStateMachine, logs industry/kernel/pod info.
- `config.py` — all roles → claude_desktop, adapter_mode default → claude_desktop, added default_industry.
- `catalog.py` — default hosts → claude_desktop only, filters invalid hosts.
- `db.py` — added get_plan(plan_id) method.
- All test files updated for new API.
