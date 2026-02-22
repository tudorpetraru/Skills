---
name: Customer Update Writer
description: Drafts customer-safe updates for incidents, releases, and roadmap changes.
tags: [customer, communication, incident, release]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.scribe]
---
# Customer Update Writer
Drafts customer-safe updates for incidents, releases, and roadmap changes.
Hosts: claude_desktop,codex_desktop
Tags: customer,communication,incident,release
Depends-On: core.scribe
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
