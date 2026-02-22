---
name: Model Selection
description: Selects model families based on task profile, latency, and cost constraints.
tags: [ai, models, selection, cost]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Model Selection
Selects model families based on task profile, latency, and cost constraints.
Hosts: claude_desktop,codex_desktop
Tags: ai,models,selection,cost
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
