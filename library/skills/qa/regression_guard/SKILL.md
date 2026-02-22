---
name: Regression Guard
description: Builds regression protection plans and failure triage routes.
tags: [regression, qa, stability, quality]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Regression Guard
Builds regression protection plans and failure triage routes.
Hosts: claude_desktop,codex_desktop
Tags: regression,qa,stability,quality
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
