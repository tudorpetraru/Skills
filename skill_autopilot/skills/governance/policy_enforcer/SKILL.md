---
name: Policy Enforcer
description: Translates policy requirements into enforceable operational controls.
tags: [policy, controls, compliance, governance]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.quality]
---
# Policy Enforcer
Translates policy requirements into enforceable operational controls.
Hosts: claude_desktop,codex_desktop
Tags: policy,controls,compliance,governance
Depends-On: core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
