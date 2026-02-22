---
name: Roadmap Planner
description: Builds phased roadmaps aligned to outcomes, risks, and dependencies.
tags: [roadmap, planning, milestones, delivery]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Roadmap Planner
Builds phased roadmaps aligned to outcomes, risks, and dependencies.
Hosts: claude_desktop,codex_desktop
Tags: roadmap,planning,milestones,delivery
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
