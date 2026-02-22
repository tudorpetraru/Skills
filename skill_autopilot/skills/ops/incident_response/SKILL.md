---
name: Incident Response
description: Handles production incidents with triage, containment, and communication workflows.
tags: [incident, operations, triage, reliability]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.scribe]
---

# Incident Response

Provide structured response for service-impacting incidents.

Hosts: claude_desktop,codex_desktop
Tags: incident,operations,triage,reliability
Depends-On: core.orchestrator,core.scribe

## Workflow
1. Classify severity and impact.
2. Assign incident commander and responders.
3. Track mitigation timeline and stakeholder updates.
4. Record actions for post-incident review.
