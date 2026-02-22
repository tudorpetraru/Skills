---
name: Requirements Specifier
description: Produces decision-complete functional and non-functional requirements from normalized intent.
tags: [requirements, specification, acceptance, scope]
hosts: [claude_desktop, codex_desktop]
dependencies: [discovery.brief_normalizer, core.quality]
---

# Requirements Specifier

Generate implementation-ready requirements and acceptance criteria.

Hosts: claude_desktop,codex_desktop
Tags: requirements,specification,acceptance,scope
Depends-On: discovery.brief_normalizer,core.quality

## Output Contract
1. In-scope/out-of-scope boundaries.
2. Functional requirements by capability.
3. Non-functional requirements (latency, reliability, security).
4. Acceptance tests mapped to requirements.
