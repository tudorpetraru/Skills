---
name: Risk and Compliance
description: Classifies project risk, applies governance controls, and defines required approvals.
tags: [risk, compliance, governance, controls]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.quality]
---

# Risk and Compliance

Attach governance intensity to project risk level.

Hosts: claude_desktop,codex_desktop
Tags: risk,compliance,governance,controls
Depends-On: core.quality

## Outputs
1. Risk register with severity and owner.
2. Required approvals by phase.
3. Control checklist tied to release gates.
