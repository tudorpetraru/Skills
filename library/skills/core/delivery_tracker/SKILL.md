---
name: Delivery Tracker
description: Tracks milestones, dependencies, and timeline drift with clear escalation triggers.
tags: [delivery, milestones, dependencies, status]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator]
---

# Delivery Tracker

Maintain a real-time delivery view for milestones and blockers.

Hosts: claude_desktop,codex_desktop
Tags: delivery,milestones,timeline,escalation
Depends-On: core.orchestrator

## Outputs
1. Milestone board with owners and due dates.
2. Dependency risk report.
3. Escalation alerts for critical-path slips.
