---
name: Brief Normalizer
description: Transforms free-form briefs into normalized goals, constraints, deliverables, and risk profiles.
tags: [discovery, brief, normalization, requirements]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator]
---

# Brief Normalizer

Convert raw project briefs into structured intent with minimal ambiguity.

Hosts: claude_desktop,codex_desktop
Tags: discovery,brief,intent,structure
Depends-On: core.orchestrator

## Required Output Fields
1. Goals
2. Constraints
3. Deliverables
4. Risk tier
5. Evidence level
