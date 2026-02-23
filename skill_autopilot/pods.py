"""Pod architecture: Core + attachable pods + B-kernel families + industry mapping.

Maps directly to project_brief.md §3–§5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Sequence


@dataclass(frozen=True)
class PodSpec:
    """A capability pod — a bundle of agents for a project area."""
    pod_id: str
    name: str
    agents: tuple[str, ...]
    always_on: bool = False
    description: str = ""


@dataclass(frozen=True)
class KernelSpec:
    """A Build & Ship kernel variant — stable interface, domain-specific."""
    kernel_id: str
    name: str
    description: str
    skill_category: str = "kernel"
    required_skills: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# §3.1 — Core pod (always-on)
# ---------------------------------------------------------------------------

CORE_POD = PodSpec(
    pod_id="core",
    name="Core",
    always_on=True,
    description="Always-on project foundation: orchestration, documentation, research, quality, and delivery tracking.",
    agents=(
        "orchestrator",
        "scribe",
        "research",
        "quality",
        "delivery_tracker",
    ),
)


# ---------------------------------------------------------------------------
# §3.2 — Attachable pods
# ---------------------------------------------------------------------------

DISCOVERY_POD = PodSpec(
    pod_id="discovery",
    name="Discovery & Definition",
    description="Requirements clarification, competitor analysis, user research, and feasibility checks.",
    agents=(
        "requirements_specifier",
        "competitor_analyst",
        "user_researcher",
        "feasibility_assessor",
    ),
)

COMMERCIAL_POD = PodSpec(
    pod_id="commercial",
    name="Commercial",
    description="Pricing, go-to-market strategy, sales enablement, and revenue modeling.",
    agents=(
        "pricing_analyst",
        "gtm_strategist",
        "sales_enabler",
    ),
)

FINANCE_GOVERNANCE_POD = PodSpec(
    pod_id="finance_governance",
    name="Finance & Governance",
    description="Budgeting, cost control, audit compliance, and financial reporting.",
    agents=(
        "budget_planner",
        "cost_controller",
        "audit_steward",
    ),
)

LEGAL_RISK_POD = PodSpec(
    pod_id="legal_risk",
    name="Legal / Risk / Compliance",
    description="Contract review, regulatory compliance, risk assessment, and policy enforcement.",
    agents=(
        "contract_reviewer",
        "compliance_officer",
        "risk_assessor",
    ),
)

PEOPLE_TALENT_POD = PodSpec(
    pod_id="people_talent",
    name="People & Talent",
    description="Team composition, hiring plans, onboarding, and skill gap analysis.",
    agents=(
        "team_planner",
        "hiring_advisor",
        "skill_gap_analyst",
    ),
)

OPS_SUPPLY_POD = PodSpec(
    pod_id="ops_supply",
    name="Ops & Supply",
    description="Procurement, vendor management, supply chain, and operational logistics.",
    agents=(
        "procurement_agent",
        "vendor_manager",
        "logistics_planner",
    ),
)

DATA_INSIGHT_POD = PodSpec(
    pod_id="data_insight",
    name="Data & Insight",
    description="Data pipeline design, BI reporting, metrics systems, and analytics.",
    agents=(
        "data_architect",
        "bi_analyst",
        "metrics_designer",
    ),
)

ALL_ATTACHABLE_PODS: Dict[str, PodSpec] = {
    pod.pod_id: pod
    for pod in [
        DISCOVERY_POD,
        COMMERCIAL_POD,
        FINANCE_GOVERNANCE_POD,
        LEGAL_RISK_POD,
        PEOPLE_TALENT_POD,
        OPS_SUPPLY_POD,
        DATA_INSIGHT_POD,
    ]
}


# ---------------------------------------------------------------------------
# §4 — B-kernel families (Build & Ship)
# ---------------------------------------------------------------------------

B_KERNELS: Dict[str, KernelSpec] = {}

_KERNEL_DEFS = [
    ("digital_product", "B-Digital Product",
     "Apps, SaaS, platforms — iterative software delivery.",
     ("software", "product", "build", "ship")),
    ("data_analytics", "B-Data & Analytics",
     "Pipelines, BI, metrics systems, and data platforms.",
     ("data", "analytics", "pipeline", "bi")),
    ("ml_ai_systems", "B-ML/AI Systems",
     "Model lifecycle, evaluation, monitoring, and ML ops.",
     ("ml", "ai", "model", "evaluation")),
    ("cyber_secops", "B-Cyber & SecOps",
     "Detections, incident response, hardening, security operations.",
     ("security", "cyber", "incident", "detection")),
    ("embedded_mechatronics", "B-Embedded & Mechatronics",
     "Firmware, sensors, controls, and embedded systems.",
     ("embedded", "firmware", "sensors", "controls")),
    ("safety_critical", "B-Safety-Critical Engineering",
     "Formal V&V, safety cases, and safety-critical systems.",
     ("safety", "critical", "verification", "validation")),
    ("industrial_manufacturing", "B-Industrial Manufacturing",
     "Process engineering, industrialization, and manufacturing.",
     ("manufacturing", "process", "industrialization")),
    ("chem_materials", "B-Chem/Materials Process",
     "Formulations, scale-up, QA evidence for chemical/materials.",
     ("chemistry", "materials", "formulation", "scale-up")),
    ("life_sciences", "B-Life Sciences R&D to Regulated",
     "Evidence chains, GLxP-style discipline, regulated R&D.",
     ("life_sciences", "pharma", "biotech", "regulated")),
    ("energy_asset_ops", "B-Energy & Asset Ops",
     "Asset operations, reliability, and field work.",
     ("energy", "asset", "reliability", "field")),
    ("financial_products", "B-Financial Products & Controls",
     "Auditability, risk, models, reporting for financial products.",
     ("finance", "risk", "audit", "reporting")),
    ("construction_infra", "B-Construction & Infrastructure",
     "Permits, schedule/cost, site safety, and infrastructure.",
     ("construction", "infrastructure", "permits", "civil")),
    ("content_production", "B-Content Production",
     "Media, publishing, brand assets, and content workflows.",
     ("content", "media", "publishing", "brand")),
    ("professional_services", "B-Professional Services Delivery",
     "SoW, client governance, delivery ops, and service engagements.",
     ("services", "consulting", "client", "delivery")),
]

for _kid, _kname, _kdesc, _ktags in _KERNEL_DEFS:
    B_KERNELS[_kid] = KernelSpec(
        kernel_id=_kid,
        name=_kname,
        description=_kdesc,
        tags=_ktags,
    )


# ---------------------------------------------------------------------------
# §5 — Industry → default B-kernel mapping (40 industries)
# ---------------------------------------------------------------------------

INDUSTRY_KERNEL_MAP: Dict[str, List[str]] = {
    "Software / SaaS": ["digital_product"],
    "IT Services / Systems Integration": ["professional_services"],
    "Cloud / Data Centers": ["energy_asset_ops", "digital_product"],
    "Cybersecurity (vendors)": ["digital_product", "cyber_secops"],
    "Telecommunications": ["energy_asset_ops", "digital_product"],
    "Semiconductors": ["industrial_manufacturing", "safety_critical"],
    "Consumer Electronics": ["embedded_mechatronics", "industrial_manufacturing"],
    "Automotive (OEM & mobility)": ["embedded_mechatronics", "safety_critical"],
    "Rail / Transit": ["safety_critical", "construction_infra"],
    "Aerospace": ["safety_critical", "embedded_mechatronics"],
    "Space (launch/satellites)": ["safety_critical", "embedded_mechatronics"],
    "Defense": ["safety_critical", "cyber_secops"],
    "Maritime / Shipping": ["energy_asset_ops", "construction_infra"],
    "Logistics / 3PL": ["construction_infra", "data_analytics"],
    "Retail (physical)": ["data_analytics", "digital_product"],
    "E-commerce / Marketplaces": ["digital_product", "data_analytics"],
    "Consumer Packaged Goods (CPG)": ["industrial_manufacturing", "data_analytics"],
    "Food & Beverage Manufacturing": ["industrial_manufacturing", "chem_materials"],
    "Agriculture": ["industrial_manufacturing", "data_analytics"],
    "Mining & Metals": ["energy_asset_ops", "industrial_manufacturing"],
    "Oil & Gas (upstream)": ["energy_asset_ops"],
    "Oil & Gas (midstream)": ["energy_asset_ops"],
    "Refining / Petrochemicals": ["chem_materials", "industrial_manufacturing"],
    "Chemicals (specialty/commodity)": ["chem_materials"],
    "Materials (advanced materials)": ["chem_materials"],
    "Construction (GC / EPC)": ["construction_infra"],
    "Real Estate (dev/property mgmt)": ["construction_infra", "energy_asset_ops"],
    "Utilities (electric/gas/water)": ["energy_asset_ops"],
    "Power generation (incl. nuclear)": ["energy_asset_ops", "safety_critical"],
    "Renewables (wind/solar/storage)": ["energy_asset_ops", "embedded_mechatronics"],
    "Healthcare Providers (hospitals/clinics)": ["life_sciences", "data_analytics"],
    "Health Insurance / Payers": ["financial_products", "data_analytics"],
    "Medical Devices": ["safety_critical", "life_sciences"],
    "Pharmaceuticals": ["life_sciences"],
    "Biotech": ["life_sciences"],
    "CRO / Clinical Trials Services": ["life_sciences", "professional_services"],
    "Banking (retail/commercial)": ["financial_products"],
    "Payments / Fintech": ["financial_products", "digital_product"],
    "Insurance": ["financial_products", "data_analytics"],
    "Capital Markets / Asset Mgmt": ["financial_products", "ml_ai_systems"],
}


# ---------------------------------------------------------------------------
# Pod selection logic
# ---------------------------------------------------------------------------

# Keywords that suggest attaching a particular pod.
_POD_SIGNAL_KEYWORDS: Dict[str, List[str]] = {
    "discovery": ["requirements", "research", "competitor", "feasibility", "discovery", "user research", "market"],
    "commercial": ["pricing", "go-to-market", "revenue", "sales", "commercial", "monetiz"],
    "finance_governance": ["budget", "cost", "audit", "financial report", "governance", "sox"],
    "legal_risk": ["compliance", "regulatory", "legal", "contract", "risk", "gdpr", "hipaa"],
    "people_talent": ["hiring", "onboard", "team", "talent", "staffing", "skill gap"],
    "ops_supply": ["procurement", "vendor", "supply chain", "logistics", "sourcing"],
    "data_insight": ["data pipeline", "analytics", "bi ", "dashboard", "metrics", "reporting"],
}


def select_pods(
    intent_text: str,
    industry: str = "",
    pod_hints: Sequence[str] = (),
) -> Dict[str, PodSpec]:
    """Select pods for a project based on brief text, industry, and explicit hints.

    Always includes Core pod. Returns dict of pod_id -> PodSpec.
    """
    selected: Dict[str, PodSpec] = {"core": CORE_POD}

    # Always include discovery — every project benefits from clarification.
    selected["discovery"] = DISCOVERY_POD

    # Explicit hints from brief or user.
    for hint in pod_hints:
        hint_lower = hint.strip().lower().replace(" ", "_")
        if hint_lower in ALL_ATTACHABLE_PODS:
            selected[hint_lower] = ALL_ATTACHABLE_PODS[hint_lower]

    # Keyword-based pod attachment.
    text_lower = intent_text.lower()
    for pod_id, keywords in _POD_SIGNAL_KEYWORDS.items():
        if pod_id in selected:
            continue
        if any(kw in text_lower for kw in keywords):
            selected[pod_id] = ALL_ATTACHABLE_PODS[pod_id]

    return selected


def select_kernels(
    industry: str = "",
    intent_text: str = "",
    explicit_kernels: Sequence[str] = (),
) -> List[KernelSpec]:
    """Select B-kernels for a project. Uses industry mapping + text signals.

    Falls back to B-Digital Product if nothing matches.
    """
    kernel_ids: list[str] = []

    # Explicit kernel requests.
    for kid in explicit_kernels:
        kid_clean = kid.strip().lower().replace("-", "_").replace(" ", "_")
        if kid_clean in B_KERNELS:
            kernel_ids.append(kid_clean)

    # Industry mapping.
    if industry:
        for industry_name, kid_list in INDUSTRY_KERNEL_MAP.items():
            if industry.lower().strip() in industry_name.lower():
                kernel_ids.extend(kid_list)
                break

    # Text-signal fallback: look for kernel tags in the brief.
    if not kernel_ids:
        text_lower = intent_text.lower()
        for kid, kspec in B_KERNELS.items():
            if any(tag in text_lower for tag in kspec.tags):
                kernel_ids.append(kid)
                if len(kernel_ids) >= 2:
                    break

    # Ultimate fallback.
    if not kernel_ids:
        kernel_ids.append("digital_product")

    # Deduplicate while preserving order.
    seen: set[str] = set()
    result: list[KernelSpec] = []
    for kid in kernel_ids:
        if kid not in seen and kid in B_KERNELS:
            seen.add(kid)
            result.append(B_KERNELS[kid])
    return result


def detect_industry(text: str) -> str:
    """Detect industry from brief text.

    Two-tier approach:
      1. LLM classification via Anthropic API (when ANTHROPIC_API_KEY is set).
      2. Weighted keyword scoring fallback.
    """
    # Tier 1: LLM classification (fast, precise).
    llm_result = _detect_industry_llm(text)
    if llm_result:
        return llm_result

    # Tier 2: Weighted keyword scoring.
    return _detect_industry_keywords(text)


def _detect_industry_llm(text: str) -> str:
    """Classify industry using Claude Haiku. Returns empty string on failure."""
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return ""

    try:
        import anthropic  # noqa: F811
    except ImportError:
        return ""

    industries = list(INDUSTRY_KERNEL_MAP.keys())
    industries_text = "\n".join(f"- {name}" for name in industries)

    prompt = (
        "You are an industry classifier. Given a project brief, identify the single "
        "best-matching industry from the list below. Reply with ONLY the industry name, "
        "exactly as written. If none match well, reply NONE.\n\n"
        f"Industries:\n{industries_text}\n\n"
        f"Project brief:\n{text[:3000]}"
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-20250414",
            max_tokens=80,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = message.content[0].text.strip()
        if answer == "NONE" or answer not in INDUSTRY_KERNEL_MAP:
            # Try fuzzy match (LLM might slightly rephrase).
            answer_lower = answer.lower()
            for name in industries:
                if answer_lower in name.lower() or name.lower() in answer_lower:
                    return name
            return ""
        return answer
    except Exception:
        return ""


# Weighted keyword signals: (keyword, weight).
# Higher weight = more specific signal. Generic terms get low weight.
_INDUSTRY_SIGNALS_WEIGHTED: list[tuple[str, list[tuple[str, float]]]] = [
    ("Pharmaceuticals", [
        ("pharmaceutical", 1.0), ("drug development", 1.0), ("clinical trial", 0.8),
        ("fda approval", 0.9), ("drug candidate", 1.0), ("pharma", 0.9),
    ]),
    ("Biotech", [
        ("biotech", 1.0), ("gene therapy", 1.0), ("cell therapy", 1.0),
        ("biologic", 0.8), ("crispr", 1.0),
    ]),
    ("Medical Devices", [
        ("medical device", 1.0), ("class ii", 0.8), ("class iii", 0.8),
        ("510(k)", 1.0), ("implant", 0.6),
    ]),
    ("CRO / Clinical Trials Services", [
        ("cro ", 0.9), ("contract research", 1.0), ("clinical trial manage", 0.9),
    ]),
    ("Healthcare Providers (hospitals/clinics)", [
        ("hospital", 0.8), ("clinic", 0.7), ("healthcare provider", 1.0),
        ("patient care", 0.9), ("patient intake", 0.9), ("ehr ", 0.8),
        ("electronic health", 0.9), ("dental", 0.8), ("medical practice", 0.9),
        ("telemedicine", 0.9), ("telehealth", 0.9), ("health record", 0.8),
        ("doctor", 0.5), ("nurse", 0.5), ("appointment", 0.4),
    ]),
    ("Health Insurance / Payers", [
        ("health insurance", 1.0), ("payer", 0.7), ("claims processing", 1.0),
    ]),
    ("Capital Markets / Asset Mgmt", [
        ("capital market", 1.0), ("asset management", 0.9), ("trading", 0.7),
        ("portfolio", 0.6), ("hedge fund", 1.0), ("quant", 0.7),
    ]),
    ("Banking (retail/commercial)", [
        ("banking", 0.8), ("retail bank", 1.0), ("commercial bank", 1.0),
        ("loan origination", 0.9), ("deposit", 0.5), ("mortgage", 0.8),
    ]),
    ("Payments / Fintech", [
        ("payment processing", 1.0), ("fintech", 1.0), ("neobank", 1.0),
        ("payment gateway", 0.9), ("digital wallet", 0.9), ("stripe", 0.6),
        ("checkout", 0.5),
    ]),
    ("Insurance", [
        ("insurance", 0.8), ("underwriting", 1.0), ("actuarial", 1.0),
        ("claims", 0.5), ("policy premium", 0.9),
    ]),
    ("Cybersecurity (vendors)", [
        ("cybersecurity", 1.0), ("threat detection", 1.0), ("soc ", 0.7),
        ("siem", 1.0), ("vulnerability", 0.6), ("pentest", 0.8),
    ]),
    ("Semiconductors", [
        ("semiconductor", 1.0), ("chip design", 1.0), ("wafer", 1.0),
        ("fab ", 0.6), ("asic", 1.0), ("fpga", 0.8),
    ]),
    ("Aerospace", [
        ("aerospace", 1.0), ("aircraft", 0.9), ("avionics", 1.0), ("airframe", 1.0),
    ]),
    ("Space (launch/satellites)", [
        ("satellite", 0.9), ("space launch", 1.0), ("orbit", 0.7),
    ]),
    ("Defense", [
        ("defense", 0.8), ("defence", 0.8), ("military", 0.9),
    ]),
    ("Automotive (OEM & mobility)", [
        ("automotive", 1.0), ("vehicle", 0.6), ("oem ", 0.5),
        ("adas", 1.0), ("autonomous driving", 1.0),
    ]),
    ("Rail / Transit", [
        ("rail ", 0.7), ("transit", 0.6), ("locomotive", 1.0), ("railway", 0.9),
    ]),
    ("Maritime / Shipping", [
        ("maritime", 1.0), ("shipping", 0.6), ("vessel", 0.7),
    ]),
    ("Oil & Gas (upstream)", [
        ("upstream oil", 1.0), ("drilling", 0.7), ("well ", 0.4),
        ("reservoir", 0.8), ("exploration", 0.5),
    ]),
    ("Oil & Gas (midstream)", [
        ("midstream", 1.0), ("pipeline transport", 1.0),
    ]),
    ("Refining / Petrochemicals", [
        ("refining", 0.8), ("petrochemical", 1.0), ("refinery", 1.0),
    ]),
    ("Chemicals (specialty/commodity)", [
        ("chemical", 0.7), ("specialty chemical", 1.0),
    ]),
    ("Materials (advanced materials)", [
        ("advanced material", 1.0), ("composite", 0.6), ("nanomaterial", 1.0),
    ]),
    ("Power generation (incl. nuclear)", [
        ("power generation", 1.0), ("nuclear", 0.7), ("power plant", 1.0),
    ]),
    ("Renewables (wind/solar/storage)", [
        ("renewable", 0.8), ("solar", 0.6), ("wind farm", 1.0),
        ("battery storage", 0.9),
    ]),
    ("Utilities (electric/gas/water)", [
        ("utility", 0.5), ("electric utility", 1.0), ("water utility", 1.0),
    ]),
    ("Mining & Metals", [
        ("mining", 0.8), ("ore ", 0.7), ("metal processing", 1.0),
    ]),
    ("Construction (GC / EPC)", [
        ("construction", 0.7), ("general contractor", 1.0), ("epc ", 0.8),
    ]),
    ("Real Estate (dev/property mgmt)", [
        ("real estate", 1.0), ("property management", 1.0), ("reit", 1.0),
    ]),
    ("Food & Beverage Manufacturing", [
        ("food manufacturing", 1.0), ("beverage", 0.6), ("food processing", 1.0),
        ("restaurant", 0.6), ("food service", 0.7),
    ]),
    ("Agriculture", [
        ("agriculture", 1.0), ("farming", 0.8), ("agri-tech", 1.0),
        ("agritech", 1.0), ("crop", 0.6),
    ]),
    ("Consumer Packaged Goods (CPG)", [
        ("cpg ", 1.0), ("consumer packaged", 1.0), ("fmcg", 1.0),
    ]),
    ("Consumer Electronics", [
        ("consumer electronics", 1.0), ("wearable", 0.7), ("smart device", 0.8),
    ]),
    ("Logistics / 3PL", [
        ("logistics", 0.8), ("3pl", 1.0), ("warehousing", 0.7), ("freight", 0.8),
        ("supply chain", 0.7), ("inventory", 0.5),
    ]),
    ("Retail (physical)", [
        ("retail store", 1.0), ("brick and mortar", 1.0), ("pos ", 0.6),
        ("store manager", 0.8), ("retail chain", 0.9),
    ]),
    ("E-commerce / Marketplaces", [
        ("e-commerce", 1.0), ("ecommerce", 1.0), ("marketplace", 0.7),
        ("online store", 0.9), ("shopify", 0.8),
    ]),
    ("Telecommunications", [
        ("telecom", 0.9), ("5g ", 0.8), ("network operator", 1.0),
    ]),
    ("Cloud / Data Centers", [
        ("data center", 1.0), ("cloud infrastructure", 1.0),
        ("iaas", 1.0), ("paas", 0.9),
    ]),
    ("IT Services / Systems Integration", [
        ("it service", 0.9), ("system integrat", 0.9), ("managed service", 0.9),
    ]),
    ("Software / SaaS", [
        ("saas", 1.0), ("software product", 0.8),
        # Generic terms get LOW weight — they shouldn't override specific industry signals.
        ("platform", 0.2), ("web app", 0.2), ("api", 0.15),
        ("mobile app", 0.2), ("dashboard", 0.15),
    ]),
]


def _detect_industry_keywords(text: str) -> str:
    """Score all industries and return best match.

    Multi-signal weighted scoring instead of first-match.
    A keyword like 'platform' (weight 0.2) won't override 'clinic' (weight 0.7).
    """
    text_lower = text.lower()

    best_industry = ""
    best_score = 0.0

    for industry_name, signals in _INDUSTRY_SIGNALS_WEIGHTED:
        score = sum(weight for term, weight in signals if term in text_lower)
        if score > best_score:
            best_score = score
            best_industry = industry_name

    # Require a minimum signal strength to avoid false positives.
    if best_score < 0.5:
        return ""

    return best_industry

