---
name: Daily Status Digest
description: Generates concise daily updates with blockers and next actions.
tags: [status, updates, coordination, delivery]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.scribe]
---
# Daily Status Digest
Generates concise daily updates with blockers and next actions.
Hosts: claude_desktop,codex_desktop
Tags: status,updates,coordination,delivery
Depends-On: core.scribe
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
