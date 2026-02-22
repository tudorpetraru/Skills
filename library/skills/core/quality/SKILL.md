---
name: Core Quality
description: Enforces acceptance criteria, identifies failure modes, and blocks low-quality transitions.
tags: [quality, validation, risk, testing]
hosts: [claude_desktop, codex_desktop]
---

# Core Quality

Run structured quality and risk checks before each phase transition.

Hosts: claude_desktop,codex_desktop
Tags: quality,verification,risk,gates

## Checklist
1. Validate deliverables against acceptance criteria.
2. Identify unresolved risks and severity.
3. Confirm required evidence is present.
4. Return `pass`, `pass-with-actions`, or `block`.
