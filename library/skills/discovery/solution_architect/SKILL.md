---
name: Solution Architect
description: Maps requirements to architecture choices, interfaces, and deployment boundaries.
tags: [architecture, interfaces, systems, tradeoffs]
hosts: [claude_desktop, codex_desktop]
dependencies: [discovery.requirements_specifier, core.research]
---

# Solution Architect

Create architecture decisions that are implementable and testable.

Hosts: claude_desktop,codex_desktop
Tags: architecture,interfaces,systems,tradeoffs
Depends-On: discovery.requirements_specifier,core.research

## Outputs
1. Component map and interface contracts.
2. Data flow and failure handling path.
3. Technology decisions with tradeoff rationale.
