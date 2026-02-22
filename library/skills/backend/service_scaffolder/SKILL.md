---
name: Service Scaffolder
description: Scaffolds backend service structure with production-ready defaults.
tags: [backend, services, scaffold, engineering]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Service Scaffolder
Scaffolds backend service structure with production-ready defaults.
Hosts: claude_desktop,codex_desktop
Tags: backend,services,scaffold,engineering
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
