---
name: Handoff Writer
description: Produces handoff packets for operations, support, and future project teams.
tags: [handoff, documentation, transition, operations]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.scribe, governance.evidence_packager]
---

# Handoff Writer

Create clean transition artifacts at release or project close.

Hosts: claude_desktop,codex_desktop
Tags: handoff,transition,operations,docs
Depends-On: core.scribe,governance.evidence_packager

## Handoff Packet
1. Final architecture and key decisions.
2. Operational runbook and support contacts.
3. Known risks and pending actions.
4. Evidence bundle link.
