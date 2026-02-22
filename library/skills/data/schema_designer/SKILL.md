---
name: Schema Designer
description: Designs robust data schemas with lineage and change compatibility.
tags: [data, schema, modeling, integration]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Schema Designer
Designs robust data schemas with lineage and change compatibility.
Hosts: claude_desktop,codex_desktop
Tags: data,schema,modeling,integration
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
