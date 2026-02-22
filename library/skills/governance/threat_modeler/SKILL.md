---
name: Threat Modeler
description: Builds threat models and mitigation plans for prioritized attack paths.
tags: [security, threat-modeling, risk, governance]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.quality]
---
# Threat Modeler
Builds threat models and mitigation plans for prioritized attack paths.
Hosts: claude_desktop,codex_desktop
Tags: security,threat-modeling,risk,governance
Depends-On: core.quality
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
