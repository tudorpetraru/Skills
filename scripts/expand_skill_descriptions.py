#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "library" / "skills"

CATEGORY_PROFILE: Dict[str, Dict[str, List[str] | str]] = {
    "core": {
        "mission": "cross-project orchestration, delivery control, and execution clarity",
        "responsibilities": [
            "Turn ambiguous asks into an executable, deterministic plan.",
            "Track assumptions, decisions, and unresolved questions explicitly.",
            "Expose risks early and route work to the right specialist skills.",
            "Keep context concise so downstream agents can execute without rework.",
        ],
        "workflow": [
            "Normalize objective, constraints, and success criteria.",
            "Define task graph, owners, dependencies, and acceptance gates.",
            "Publish execution packet and update cadence.",
            "Monitor drift and trigger reroute or escalation when required.",
        ],
    },
    "discovery": {
        "mission": "problem framing, context gathering, and solution-shaping",
        "responsibilities": [
            "Clarify who the user is, what problem matters, and why now.",
            "Separate assumptions from validated evidence.",
            "Define measurable outcomes before proposing implementation.",
            "Surface major unknowns and create validation tasks.",
        ],
        "workflow": [
            "Collect brief context, constraints, and stakeholders.",
            "Synthesize findings into objective statements and non-goals.",
            "Generate candidate options with tradeoffs.",
            "Recommend next discovery or execution step with evidence.",
        ],
    },
    "product": {
        "mission": "product direction, prioritization, and requirement quality",
        "responsibilities": [
            "Define product scope with explicit tradeoffs.",
            "Translate strategy into structured requirements and milestones.",
            "Link roadmap decisions to measurable outcomes.",
            "Prevent misalignment between user value and build effort.",
        ],
        "workflow": [
            "Confirm product objective and target segment.",
            "Frame options using value, risk, and effort.",
            "Produce requirement artifacts with acceptance criteria.",
            "Align handoff with design, engineering, and go-to-market needs.",
        ],
    },
    "architecture": {
        "mission": "system design, reliability, and scalability planning",
        "responsibilities": [
            "Define component boundaries and ownership contracts.",
            "Model failure modes and resilience controls.",
            "Balance performance, reliability, and cost constraints.",
            "Ensure design decisions remain operable and testable.",
        ],
        "workflow": [
            "Capture service-level requirements and constraints.",
            "Draft architecture variants and evaluate tradeoffs.",
            "Select target design with risk mitigation plan.",
            "Produce implementation and validation checklist.",
        ],
    },
    "build": {
        "mission": "implementation planning, sequencing, and execution readiness",
        "responsibilities": [
            "Break scope into deliverable work packages.",
            "Sequence tasks to reduce integration risk.",
            "Define validation and rollback checkpoints.",
            "Keep delivery plan aligned with dependencies and staffing.",
        ],
        "workflow": [
            "Review architecture and requirements context.",
            "Create dependency-aware execution backlog.",
            "Attach quality checks and release criteria to each phase.",
            "Publish implementation plan and update triggers.",
        ],
    },
    "qa": {
        "mission": "verification quality, regression prevention, and confidence building",
        "responsibilities": [
            "Design focused tests for critical paths and edge cases.",
            "Quantify quality risk instead of relying on intuition.",
            "Define entry and exit criteria for release confidence.",
            "Report failures with actionable diagnosis and ownership.",
        ],
        "workflow": [
            "Map acceptance criteria to test coverage strategy.",
            "Prioritize tests by risk and impact.",
            "Execute checks and consolidate findings.",
            "Recommend release decision with evidence summary.",
        ],
    },
    "data": {
        "mission": "data model quality, pipeline reliability, and analytical trust",
        "responsibilities": [
            "Design schema and lineage for long-term maintainability.",
            "Build data quality controls and reconciliation checks.",
            "Protect analytical correctness during change and migration.",
            "Define observability for critical data operations.",
        ],
        "workflow": [
            "Capture source systems and downstream consumers.",
            "Design schema and transformation contracts.",
            "Add validation, monitoring, and failure recovery paths.",
            "Package migration and rollback instructions.",
        ],
    },
    "ai": {
        "mission": "model quality, safety controls, and AI system reliability",
        "responsibilities": [
            "Choose model and prompting strategy based on constraints.",
            "Define evaluation harnesses with deterministic scoring.",
            "Design safety and policy controls around model behavior.",
            "Control inference cost and latency tradeoffs.",
        ],
        "workflow": [
            "Clarify task type, risk profile, and latency/cost targets.",
            "Build baseline approach and measurable evaluation plan.",
            "Add guardrails and failure handling strategy.",
            "Recommend rollout controls and continuous monitoring.",
        ],
    },
    "governance": {
        "mission": "risk, compliance, and auditability across delivery lifecycle",
        "responsibilities": [
            "Translate policy requirements into concrete controls.",
            "Track evidence needed for audit and change governance.",
            "Identify legal, operational, and security risk concentration.",
            "Escalate non-compliant paths before implementation proceeds.",
        ],
        "workflow": [
            "Identify applicable controls and obligations.",
            "Assess current-state gaps and risk severity.",
            "Define remediation path with owners and due dates.",
            "Package evidence artifacts for audit readiness.",
        ],
    },
    "ops": {
        "mission": "runtime operations, release safety, and incident readiness",
        "responsibilities": [
            "Ensure production readiness before release windows.",
            "Define observability, response, and escalation pathways.",
            "Run operational drills and failure preparedness checks.",
            "Coordinate changes with rollback and recovery plans.",
        ],
        "workflow": [
            "Review service health objectives and known risks.",
            "Prepare runbooks, alerts, and ownership mapping.",
            "Execute or simulate key operational scenarios.",
            "Publish release and incident readiness summary.",
        ],
    },
    "comms": {
        "mission": "stakeholder clarity, decision communication, and handoff quality",
        "responsibilities": [
            "Provide concise updates with signal over noise.",
            "Communicate decisions, risks, and asks with context.",
            "Tailor narrative for technical and non-technical audiences.",
            "Preserve institutional memory across transitions.",
        ],
        "workflow": [
            "Gather latest execution and risk state.",
            "Shape message by audience and decision need.",
            "Draft concise narrative with explicit asks/owners.",
            "Publish and track follow-up actions.",
        ],
    },
    "integration": {
        "mission": "external system integration reliability and contract integrity",
        "responsibilities": [
            "Define integration contracts and versioning expectations.",
            "Model retry, idempotency, and failure behavior.",
            "Mitigate vendor and dependency risk early.",
            "Provide testable integration rollout plans.",
        ],
        "workflow": [
            "Inventory systems, auth model, and contract requirements.",
            "Design connector and failure-handling pattern.",
            "Validate integration behavior in staged environments.",
            "Publish operational ownership and support runbook.",
        ],
    },
    "frontend": {
        "mission": "frontend quality, UX coherence, and client performance",
        "responsibilities": [
            "Design UI systems that are consistent and maintainable.",
            "Map user flows to clear, testable interaction states.",
            "Improve accessibility and performance as first-class quality goals.",
            "Ensure component boundaries support iterative delivery.",
        ],
        "workflow": [
            "Capture user flow and interface requirements.",
            "Design component/state model and implementation plan.",
            "Run accessibility/performance validation checks.",
            "Deliver implementation notes and handoff assets.",
        ],
    },
    "backend": {
        "mission": "backend service robustness, API quality, and data integrity",
        "responsibilities": [
            "Design reliable service behavior under failure conditions.",
            "Define API contracts with explicit error semantics.",
            "Protect data integrity and transactional correctness.",
            "Build operable services with observability and resilience.",
        ],
        "workflow": [
            "Capture functional requirements and service-level objectives.",
            "Design APIs, storage, and worker patterns.",
            "Implement failure handling and observability plan.",
            "Validate readiness with reliability checks and runbooks.",
        ],
    },
    "mobile": {
        "mission": "mobile reliability, release discipline, and app quality",
        "responsibilities": [
            "Design mobile architecture for maintainability.",
            "Control release risk through staged rollout practices.",
            "Reduce crash frequency and user-visible instability.",
            "Handle offline/sync constraints predictably.",
        ],
        "workflow": [
            "Capture platform-specific constraints and success metrics.",
            "Design architecture/release plan with checkpoints.",
            "Validate crash, offline, and sync behavior.",
            "Package rollout and rollback instructions for operations.",
        ],
    },
    "finance": {
        "mission": "financial viability, forecasting, and cost control decision support",
        "responsibilities": [
            "Build business cases linked to measurable assumptions.",
            "Model sensitivity across cost, growth, and margin variables.",
            "Recommend controls for budget and spend discipline.",
            "Translate financial analysis into actionable decisions.",
        ],
        "workflow": [
            "Gather baseline financial and operational inputs.",
            "Model scenarios and identify key drivers.",
            "Stress-test assumptions and downside cases.",
            "Publish recommendations with quantified impact.",
        ],
    },
    "legal": {
        "mission": "legal obligation clarity and implementation-safe compliance support",
        "responsibilities": [
            "Extract operational obligations from legal text.",
            "Flag high-risk clauses and implementation impact.",
            "Map legal requirements to technical/process controls.",
            "Maintain traceability from obligation to control evidence.",
        ],
        "workflow": [
            "Identify applicable legal artifacts and obligations.",
            "Translate clauses into actionable requirements.",
            "Prioritize legal risk by impact and likelihood.",
            "Publish control checklist and escalation recommendations.",
        ],
    },
    "kernel": {
        "mission": "end-to-end digital product delivery coordination",
        "responsibilities": [
            "Bridge discovery, build, verify, and ship phases.",
            "Maintain outcome alignment across specialist tracks.",
            "Resolve cross-functional dependency conflicts.",
            "Keep execution focused on value delivery.",
        ],
        "workflow": [
            "Frame the product objective and release intent.",
            "Coordinate specialist outputs into one delivery thread.",
            "Track quality/risk gates before release decisions.",
            "Publish final release readiness packet.",
        ],
    },
}

TOKEN_RESPONSIBILITIES = {
    "risk": "Quantify risk scenarios and assign mitigation owners.",
    "compliance": "Map outputs to compliance controls and evidence expectations.",
    "security": "Treat abuse and threat cases as first-class acceptance criteria.",
    "quality": "Define objective quality gates, not subjective sign-off.",
    "performance": "Attach explicit latency/throughput targets and failure thresholds.",
    "cost": "Include cost impact and optimization levers in every recommendation.",
    "release": "Validate release readiness, rollback path, and operational comms.",
    "migration": "Plan migration checkpoints with validation and rollback criteria.",
    "audit": "Ensure decision and control traceability for post-hoc review.",
    "data": "Specify data ownership, lineage, and reconciliation expectations.",
    "model": "Define model behavior expectations and monitoring triggers.",
    "prompt": "Document prompt assumptions and failure handling behavior.",
    "roadmap": "Tie roadmap sequencing to measurable outcome milestones.",
}


def parse_frontmatter(text: str) -> Tuple[List[str], Dict[str, str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], {}
    fm_lines: List[str] = ["---"]
    meta: Dict[str, str] = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        fm_lines.append(line)
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
        i += 1
    return fm_lines, meta


def parse_list(value: str) -> List[str]:
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [item.strip().strip('"').strip("'") for item in v.split(",") if item.strip()]


def norm_label(token: str) -> str:
    return token.replace("_", " ").replace("-", " ").strip()


def unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out


def render_skill(skill_file: Path) -> str:
    raw = skill_file.read_text(encoding="utf-8")
    fm_lines, meta = parse_frontmatter(raw)
    if not fm_lines:
        raise ValueError(f"Missing frontmatter in {skill_file}")

    rel = skill_file.relative_to(CATALOG)
    parts = rel.parts
    category = parts[0]
    slug = parts[1]
    skill_id = ".".join(parts[:-1])

    name = meta.get("name", norm_label(slug).title())
    description = meta.get("description", "Executes specialized project work.")
    tags = parse_list(meta.get("tags", "[]"))
    hosts = parse_list(meta.get("hosts", "[claude_desktop, codex_desktop]"))
    dependencies = parse_list(meta.get("dependencies", "[]"))

    profile = CATEGORY_PROFILE.get(category, CATEGORY_PROFILE["core"])
    mission = str(profile["mission"])
    responsibilities = list(profile["responsibilities"])
    workflow = list(profile["workflow"])

    token_sources = set(tags)
    token_sources.update(re.split(r"[_\-.]+", slug))
    token_sources.update(re.split(r"[_\-.]+", name.lower()))
    token_resps = [TOKEN_RESPONSIBILITIES[t] for t in sorted(token_sources) if t in TOKEN_RESPONSIBILITIES]

    resp_lines = unique_keep_order(
        [
            f"Own the \"{description.rstrip('.')}\" outcome for this project stream.",
            *responsibilities,
            *token_resps,
            "Produce outputs that another agent can execute without clarification loops.",
        ]
    )[:8]

    activation = unique_keep_order(
        [
            f"The brief or a task explicitly asks for: {description.rstrip('.')}.",
            f"Decisions involve {', '.join(tags[:3]) if tags else category}-related tradeoffs.",
            f"A coordination step requires specialist output from `{skill_id}`.",
            "Current plan has unresolved risks/unknowns in this domain.",
        ]
    )

    inputs = unique_keep_order(
        [
            "Normalized project objective and success criteria.",
            "Relevant constraints (security, legal, budget, timeline, staffing).",
            "Current route selection and active phase context.",
            f"Artifacts touching this domain ({category}) and related dependencies.",
            "Definition of done expected by downstream owner(s).",
        ]
    )

    output_sections = [
        "Objective snapshot and scoped decision boundary.",
        "Execution plan (ordered steps with owners/roles).",
        "Risk register (severity, mitigation, escalation trigger).",
        "Validation checklist tied to acceptance criteria.",
        "Handoff packet for next skill/owner.",
    ]

    done_checks = [
        "Output is deterministic and executable without hidden assumptions.",
        "All major tradeoffs are explicit and justified.",
        "Validation steps are concrete and measurable.",
        "Risks include mitigation and escalation owner.",
        "Handoff dependencies and next actions are clear.",
    ]

    guardrails = unique_keep_order(
        [
            "Do not invent facts, metrics, or contractual commitments.",
            "Do not bypass governance, security, or quality gates.",
            "Do not hide uncertainty; state assumptions and confidence clearly.",
            "Prefer smallest viable scope that still meets objective.",
        ]
    )

    handoff = [
        "When blocked, escalate with: blocker, impact, options, and recommended decision.",
        "Persist decisions and rationale in a traceable form for auditability.",
    ]
    if dependencies:
        handoff.insert(0, f"Coordinate with dependency skills: {', '.join(f'`{d}`' for d in dependencies)}.")
    else:
        handoff.insert(0, "Coordinate with adjacent skills selected in the active route.")

    host_line = ",".join(hosts) if hosts else "claude_desktop,codex_desktop"
    tag_line = ",".join(tags) if tags else category
    dep_line = f"\nDepends-On: {','.join(dependencies)}" if dependencies else ""

    body_lines: List[str] = [
        f"# {name}",
        "",
        "## Job Mission",
        f"You are responsible for {mission}. In this role, the primary objective is: {description.rstrip('.')} while keeping outputs actionable for multi-agent execution.",
        "",
        "## Scope and Responsibilities",
    ]
    body_lines.extend([f"{i}. {line}" for i, line in enumerate(resp_lines, start=1)])

    body_lines.extend(
        [
            "",
            "## Activation Signals",
            *(f"- {line}" for line in activation),
            "",
            "## Required Inputs",
            *(f"- {line}" for line in inputs),
            "",
            "## Working Contract",
            f"Hosts: {host_line}",
            f"Tags: {tag_line}{dep_line}",
            "",
            "## Execution Workflow",
            *(f"{i}. {line}" for i, line in enumerate(workflow, start=1)),
            "",
            "## Deliverables",
            *(f"{i}. {line}" for i, line in enumerate(output_sections, start=1)),
            "",
            "## Definition of Done",
            *(f"- {line}" for line in done_checks),
            "",
            "## Guardrails",
            *(f"- {line}" for line in guardrails),
            "",
            "## Collaboration and Handoff",
            *(f"- {line}" for line in handoff),
            "",
        ]
    )

    return "\n".join(fm_lines + [""] + body_lines).rstrip() + "\n"


def main() -> None:
    files = sorted(CATALOG.rglob("SKILL.md"))
    for skill_file in files:
        skill_file.write_text(render_skill(skill_file), encoding="utf-8")
    print(f"Expanded {len(files)} skill descriptions")


if __name__ == "__main__":
    main()
