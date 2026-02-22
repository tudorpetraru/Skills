---
name: API Contract Designer
description: Designs stable API contracts, versioning, and compatibility strategy.
tags: [api, contracts, versioning, backend]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# API Contract Designer
Designs stable API contracts, versioning, and compatibility strategy.
Hosts: claude_desktop,codex_desktop
Tags: api,contracts,versioning,backend
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
