---
name: Compliance Checklist
description: Builds implementation checklists for common compliance regimes.
tags: [compliance, checklist, governance, risk]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Compliance Checklist
Builds implementation checklists for common compliance regimes.
Hosts: claude_desktop,codex_desktop
Tags: compliance,checklist,governance,risk
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
