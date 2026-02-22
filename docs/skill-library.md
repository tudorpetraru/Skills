# Skill Library Map

Default runtime catalog root:
`<venv>/lib/pythonX.Y/site-packages/skill_autopilot/skills`

Repository source catalog:
`library/skills`

Total curated skills: **115**

## Skill Quality Standard
Each `SKILL.md` now includes a full job description contract:
1. `Job Mission`
2. `Scope and Responsibilities`
3. `Activation Signals`
4. `Required Inputs`
5. `Working Contract`
6. `Execution Workflow`
7. `Deliverables`
8. `Definition of Done`
9. `Guardrails`
10. `Collaboration and Handoff`

## Category Coverage
1. `ai`: 7 skills
2. `architecture`: 7 skills
3. `backend`: 5 skills
4. `build`: 9 skills
5. `comms`: 8 skills
6. `core`: 10 skills
7. `data`: 6 skills
8. `discovery`: 10 skills
9. `finance`: 4 skills
10. `frontend`: 5 skills
11. `governance`: 9 skills
12. `integration`: 6 skills
13. `kernel`: 1 skills
14. `legal`: 2 skills
15. `mobile`: 4 skills
16. `ops`: 9 skills
17. `product`: 7 skills
18. `qa`: 6 skills

## Representative Skills
### Ai
1. `ai.evaluation_harness`
2. `ai.finetuning_planner`
3. `ai.guardrail_designer`
4. `ai.inference_cost_optimizer`
5. `ai.model_selection`
6. `ai.prompt_engineer`
7. `...` (1 more)

### Architecture
1. `architecture.api_contract_designer`
2. `architecture.cost_architect`
3. `architecture.event_modeler`
4. `architecture.reliability_planner`
5. `architecture.scalability_planner`
6. `architecture.service_boundary_mapper`
7. `...` (1 more)

### Backend
1. `backend.api_reliability`
2. `backend.auth_implementation`
3. `backend.database_tuner`
4. `backend.queue_worker_planner`
5. `backend.service_scaffolder`

### Build
1. `build.api_implementation_planner`
2. `build.code_migration_planner`
3. `build.env_configurator`
4. `build.implementation_planner`
5. `build.integration_planner`
6. `build.refactor_planner`
7. `...` (3 more)

### Comms
1. `comms.customer_update_writer`
2. `comms.daily_status_digest`
3. `comms.decision_memo_writer`
4. `comms.executive_brief_writer`
5. `comms.handoff_checklist`
6. `comms.handoff_writer`
7. `...` (2 more)

### Core
1. `core.assumption_tracker`
2. `core.context_compactor`
3. `core.decision_log`
4. `core.delivery_tracker`
5. `core.orchestrator`
6. `core.prompt_optimizer`
7. `...` (4 more)

### Data
1. `data.bi_semantic_modeler`
2. `data.data_quality_monitor`
3. `data.migration_validator`
4. `data.pipeline_planner`
5. `data.privacy_classifier`
6. `data.schema_designer`

### Discovery
1. `discovery.acceptance_criteria_writer`
2. `discovery.brief_normalizer`
3. `discovery.competitive_scan`
4. `discovery.constraint_mapper`
5. `discovery.hypothesis_generator`
6. `discovery.problem_framer`
7. `...` (4 more)

### Finance
1. `finance.business_case_builder`
2. `finance.cost_control_advisor`
3. `finance.forecast_planner`
4. `finance.unit_economics_modeler`

### Frontend
1. `frontend.accessibility_implementer`
2. `frontend.component_planner`
3. `frontend.design_system_builder`
4. `frontend.performance_optimizer`
5. `frontend.ui_flow_mapper`

### Governance
1. `governance.access_control_designer`
2. `governance.audit_readiness`
3. `governance.change_control`
4. `governance.data_retention_planner`
5. `governance.evidence_packager`
6. `governance.policy_enforcer`
7. `...` (3 more)

### Integration
1. `integration.api_connector_builder`
2. `integration.billing_connector`
3. `integration.identity_federation`
4. `integration.mcp_adapter_builder`
5. `integration.third_party_assessor`
6. `integration.webhook_orchestrator`

### Kernel
1. `kernel.digital_product`

### Legal
1. `legal.compliance_checklist`
2. `legal.contract_review_support`

### Mobile
1. `mobile.app_architect`
2. `mobile.crash_analyst`
3. `mobile.offline_sync_designer`
4. `mobile.release_manager`

### Ops
1. `ops.capacity_planner`
2. `ops.change_manager`
3. `ops.drill_facilitator`
4. `ops.incident_response`
5. `ops.monitoring_blueprint`
6. `ops.oncall_planner`
7. `...` (3 more)

### Product
1. `product.experiment_designer`
2. `product.feature_spec_writer`
3. `product.metric_tree`
4. `product.prd_writer`
5. `product.prioritization_rice`
6. `product.release_notes_writer`
7. `...` (1 more)

### Qa
1. `qa.accessibility_auditor`
2. `qa.performance_tester`
3. `qa.regression_guard`
4. `qa.security_tester`
5. `qa.test_case_designer`
6. `qa.usability_tester`

## Routing Policy Defaults
1. Prefer source repo: `local_library`.
2. Exclude `.system*` skill IDs.
3. Penalize utility skills unless explicitly requested.
4. Cap utility and per-cluster selections.
