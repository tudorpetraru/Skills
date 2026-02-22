---
name: Test Case Designer
description: Designs high-value test cases for critical paths and edge cases.
tags: [testing, qa, coverage, quality]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality]
---
# Test Case Designer
Designs high-value test cases for critical paths and edge cases.
Hosts: claude_desktop,codex_desktop
Tags: testing,qa,coverage,quality
Depends-On: core.orchestrator,core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
