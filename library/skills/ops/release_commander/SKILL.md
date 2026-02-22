---
name: Release Commander
description: Orchestrates release execution windows and rollback readiness.
tags: [release, operations, coordination, delivery]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Release Commander
Orchestrates release execution windows and rollback readiness.
Hosts: claude_desktop,codex_desktop
Tags: release,operations,coordination,delivery
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
