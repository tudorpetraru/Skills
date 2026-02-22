---
name: Decision Memo Writer
description: Produces decision memos with options, tradeoffs, and recommendations.
tags: [decision, memo, governance, communication]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.scribe]
---
# Decision Memo Writer
Produces decision memos with options, tradeoffs, and recommendations.
Hosts: claude_desktop,codex_desktop
Tags: decision,memo,governance,communication
Depends-On: core.scribe
## Workflow
1. Confirm project objective and constraints for this domain.
2. Produce a deterministic plan with explicit assumptions.
3. Define verification steps and failure/rollback handling.
## Outputs
1. Action checklist with clear owners or agent roles.
2. Risks and mitigations tied to acceptance criteria.
3. A concise handoff summary suitable for orchestration.
