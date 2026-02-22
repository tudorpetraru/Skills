---
name: Postmortem
description: Produces blameless postmortems with root cause and corrective action tracking.
tags: [postmortem, rca, corrective-actions, learning]
hosts: [claude_desktop, codex_desktop]
dependencies: [ops.incident_response, core.quality]
---

# Postmortem

Convert incidents into durable corrective actions.

Hosts: claude_desktop,codex_desktop
Tags: postmortem,rca,learning,quality
Depends-On: ops.incident_response,core.quality

## Required Sections
1. Timeline.
2. Root cause and contributing factors.
3. Corrective and preventive actions.
4. Owners and due dates.
