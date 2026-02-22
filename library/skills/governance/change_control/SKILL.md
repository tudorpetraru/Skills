---
name: Change Control
description: Enforces change review, impact analysis, and traceability for material project changes.
tags: [change-control, traceability, approvals, governance]
hosts: [claude_desktop, codex_desktop]
dependencies: [governance.risk_compliance, core.scribe]
---

# Change Control

Manage material changes without losing delivery integrity.

Hosts: claude_desktop,codex_desktop
Tags: change-control,impact,approvals,traceability
Depends-On: governance.risk_compliance,core.scribe

## Rules
1. Every material change needs impact analysis.
2. Assign approver and deadline.
3. Link changed items to prior decisions and affected tests.
