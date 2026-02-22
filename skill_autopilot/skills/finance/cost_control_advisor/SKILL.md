---
name: Cost Control Advisor
description: Identifies cost drivers and proposes controllable reductions.
tags: [cost, optimization, finance, operations]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Cost Control Advisor
Identifies cost drivers and proposes controllable reductions.
Hosts: claude_desktop,codex_desktop
Tags: cost,optimization,finance,operations
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
