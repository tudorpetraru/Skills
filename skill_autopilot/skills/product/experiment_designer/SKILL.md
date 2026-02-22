---
name: Experiment Designer
description: Designs product experiments with controls, hypotheses, and success thresholds.
tags: [experiments, ab-testing, metrics, validation]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Experiment Designer
Designs product experiments with controls, hypotheses, and success thresholds.
Hosts: claude_desktop,codex_desktop
Tags: experiments,ab-testing,metrics,validation
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
