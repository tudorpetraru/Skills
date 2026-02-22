---
name: Evidence Packager
description: Produces audit-ready evidence bundles for phase transitions and project closure.
tags: [evidence, audit, traceability, quality]
hosts: [claude_desktop, codex_desktop]
dependencies: [governance.change_control, core.scribe, core.quality]
---

# Evidence Packager

Assemble complete evidence bundles for each readiness gate.

Hosts: claude_desktop,codex_desktop
Tags: evidence,audit,traceability,gates
Depends-On: governance.change_control,core.scribe,core.quality

## Required Bundle
1. Decision log snapshot.
2. Change approvals and impact records.
3. Test/verification summaries.
4. Release or closure sign-off record.
