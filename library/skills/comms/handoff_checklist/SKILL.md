---
name: Handoff Checklist
description: Builds handoff checklists to transfer context across teams reliably.
tags: [handoff, checklist, operations, continuity]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.scribe]
---
# Handoff Checklist
Builds handoff checklists to transfer context across teams reliably.
Hosts: claude_desktop,codex_desktop
Tags: handoff,checklist,operations,continuity
Depends-On: core.scribe
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
