---
name: Privacy Classifier
description: Classifies data sensitivity and required handling controls.
tags: [privacy, classification, governance, security]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Privacy Classifier
Classifies data sensitivity and required handling controls.
Hosts: claude_desktop,codex_desktop
Tags: privacy,classification,governance,security
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
