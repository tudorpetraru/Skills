---
name: Component Planner
description: Plans reusable component architecture and ownership boundaries.
tags: [components, frontend, architecture, scalability]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Component Planner
Plans reusable component architecture and ownership boundaries.
Hosts: claude_desktop,codex_desktop
Tags: components,frontend,architecture,scalability
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
