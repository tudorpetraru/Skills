---
name: Capacity Planner
description: Forecasts capacity and scales infrastructure before saturation.
tags: [capacity, forecasting, reliability, ops]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Capacity Planner
Forecasts capacity and scales infrastructure before saturation.
Hosts: claude_desktop,codex_desktop
Tags: capacity,forecasting,reliability,ops
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
