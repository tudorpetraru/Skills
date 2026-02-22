---
name: Drill Facilitator
description: Plans and runs game days and failure simulation drills.
tags: [drills, resilience, ops, training]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Drill Facilitator
Plans and runs game days and failure simulation drills.
Hosts: claude_desktop,codex_desktop
Tags: drills,resilience,ops,training
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
