---
name: Service Boundary Mapper
description: Defines service ownership boundaries and integration contracts.
tags: [services, boundaries, microservices, design]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Service Boundary Mapper
Defines service ownership boundaries and integration contracts.
Hosts: claude_desktop,codex_desktop
Tags: services,boundaries,microservices,design
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
