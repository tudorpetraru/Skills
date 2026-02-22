---
name: Digital Product Kernel
description: End-to-end build-and-ship kernel for software products with iterative delivery.
tags: [software, product, build, ship, kernel]
hosts: [claude_desktop, codex_desktop]
dependencies: [core.orchestrator, core.quality, discovery.requirements_specifier]
---

# Digital Product Kernel

Default kernel for SaaS/app/platform delivery.

Hosts: claude_desktop,codex_desktop
Tags: software,product,build,ship,kernel
Depends-On: core.orchestrator,core.quality,discovery.requirements_specifier

## Required Capabilities
1. Requirement-to-plan translation.
2. Implementation sequencing.
3. Verification and release gating.
4. Traceable change and defect handling.
