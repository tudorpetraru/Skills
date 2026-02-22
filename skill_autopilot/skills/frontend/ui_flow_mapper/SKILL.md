---
name: UI Flow Mapper
description: Maps user journeys and interaction flows for product surfaces.
tags: [ux, flows, frontend, design]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# UI Flow Mapper
Maps user journeys and interaction flows for product surfaces.
Hosts: claude_desktop,codex_desktop
Tags: ux,flows,frontend,design
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
