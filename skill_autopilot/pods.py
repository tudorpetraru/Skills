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
    """Best-effort industry detection from brief text.

    Returns the matching industry name or empty string.
    """
    text_lower = text.lower()

    # Ordered from most specific to least specific.
    _INDUSTRY_SIGNALS: list[tuple[str, list[str]]] = [
        ("Pharmaceuticals", ["pharmaceutical", "drug development", "clinical trial", "fda"]),
        ("Biotech", ["biotech", "gene therapy", "cell therapy"]),
        ("Medical Devices", ["medical device", "class ii", "class iii", "510(k)"]),
        ("CRO / Clinical Trials Services", ["cro ", "contract research"]),
        ("Healthcare Providers (hospitals/clinics)", ["hospital", "clinic", "healthcare provider", "patient care"]),
        ("Health Insurance / Payers", ["health insurance", "payer", "claims processing"]),
        ("Capital Markets / Asset Mgmt", ["capital market", "asset management", "trading", "portfolio"]),
        ("Banking (retail/commercial)", ["banking", "bank ", "retail bank", "commercial bank"]),
        ("Payments / Fintech", ["payment", "fintech", "neobank"]),
        ("Insurance", ["insurance", "underwriting", "actuarial"]),
        ("Cybersecurity (vendors)", ["cybersecurity", "threat detection", "soc ", "siem"]),
        ("Semiconductors", ["semiconductor", "chip design", "wafer", "fab "]),
        ("Aerospace", ["aerospace", "aircraft", "avionics"]),
        ("Space (launch/satellites)", ["satellite", "space launch", "orbit"]),
        ("Defense", ["defense", "defence", "military"]),
        ("Automotive (OEM & mobility)", ["automotive", "vehicle", "oem ", "adas"]),
        ("Rail / Transit", ["rail ", "transit", "locomotive"]),
        ("Maritime / Shipping", ["maritime", "shipping", "vessel"]),
        ("Oil & Gas (upstream)", ["upstream oil", "exploration", "drilling", "well "]),
        ("Oil & Gas (midstream)", ["midstream", "pipeline transport"]),
        ("Refining / Petrochemicals", ["refining", "petrochemical", "refinery"]),
        ("Chemicals (specialty/commodity)", ["chemical", "specialty chemical"]),
        ("Materials (advanced materials)", ["advanced material", "composite", "nanomaterial"]),
        ("Power generation (incl. nuclear)", ["power generation", "nuclear", "power plant"]),
        ("Renewables (wind/solar/storage)", ["renewable", "solar", "wind farm", "battery storage"]),
        ("Utilities (electric/gas/water)", ["utility", "electric utility", "water utility"]),
        ("Mining & Metals", ["mining", "ore ", "metal processing"]),
        ("Construction (GC / EPC)", ["construction", "general contractor", "epc "]),
        ("Real Estate (dev/property mgmt)", ["real estate", "property management", "reit"]),
        ("Food & Beverage Manufacturing", ["food manufacturing", "beverage", "food processing"]),
        ("Agriculture", ["agriculture", "farming", "agri-tech", "agritech"]),
        ("Consumer Packaged Goods (CPG)", ["cpg ", "consumer packaged", "fmcg"]),
        ("Consumer Electronics", ["consumer electronics", "wearable", "smart device"]),
        ("Logistics / 3PL", ["logistics", "3pl", "warehousing", "freight"]),
        ("Retail (physical)", ["retail store", "brick and mortar", "pos "]),
        ("E-commerce / Marketplaces", ["e-commerce", "ecommerce", "marketplace", "online store"]),
        ("Telecommunications", ["telecom", "5g ", "network operator"]),
        ("Cloud / Data Centers", ["data center", "cloud infrastructure", "iaas", "paas"]),
        ("IT Services / Systems Integration", ["it service", "system integrat", "managed service"]),
        ("Software / SaaS", ["saas", "software product", "platform", "web app", "api"]),
    ]

    for industry_name, signals in _INDUSTRY_SIGNALS:
        if any(sig in text_lower for sig in signals):
            return industry_name

    return ""
