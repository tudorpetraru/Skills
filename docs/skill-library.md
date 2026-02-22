# Skill Library Map

Default runtime catalog root:
`<venv>/lib/pythonX.Y/site-packages/skill_autopilot/skills`

Repository source catalog:
`library/skills`

## Core
1. `core.orchestrator`
2. `core.scribe`
3. `core.research`
4. `core.quality`
5. `core.delivery_tracker`

## Discovery
1. `discovery.brief_normalizer`
2. `discovery.requirements_specifier`
3. `discovery.solution_architect`

## Governance
1. `governance.risk_compliance`
2. `governance.change_control`
3. `governance.evidence_packager`

## Kernel
1. `kernel.digital_product`

## Build
1. `build.implementation_planner`
2. `build.test_strategy`
3. `build.release_readiness`

## Ops
1. `ops.incident_response`
2. `ops.postmortem`

## Comms
1. `comms.stakeholder_updates`
2. `comms.handoff_writer`

## Routing Policy Defaults
1. Prefer source repo: `local_library`.
2. Exclude `.system*` skill IDs.
3. Penalize utility skills unless explicitly requested.
4. Cap utility and per-cluster selections.
