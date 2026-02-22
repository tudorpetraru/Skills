from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Sequence, Set, Tuple
from uuid import uuid4

from .models import BriefIntent, RouteResult, RoutingPolicy, SkillMetadata, SkillReason
from .utils import canonical_json, sha256_hex


@dataclass
class SkillScore:
    skill: SkillMetadata
    score: float
    reason: str
    utility: bool = False
    explicitly_requested: bool = False


def _tokens(text: str) -> Set[str]:
    return {token.lower() for token in text.replace("_", " ").replace("-", " ").replace(".", " ").split() if token}


def _is_utility_skill(skill: SkillMetadata, policy: RoutingPolicy) -> bool:
    sid = skill.skill_id.lower()
    configured = [entry.lower() for entry in policy.utility_skill_ids]
    return any(sid == entry or sid.endswith(f".{entry}") for entry in configured)


def _is_excluded_skill(skill: SkillMetadata, policy: RoutingPolicy) -> bool:
    return any(skill.skill_id.startswith(prefix) for prefix in policy.exclude_id_prefixes)


def _explicitly_requested(intent: BriefIntent, skill: SkillMetadata, policy: RoutingPolicy) -> bool:
    intent_tokens = _tokens(intent.raw_text)
    allow_terms = {term.lower() for term in policy.utility_allow_terms}

    skill_tokens = _tokens(skill.skill_id) | _tokens(skill.name)
    return bool(skill_tokens & allow_terms & intent_tokens)


def _score_skill(intent: BriefIntent, skill: SkillMetadata, host_targets: Sequence[str], policy: RoutingPolicy) -> SkillScore:
    intent_tokens = _tokens(intent.raw_text)
    skill_tokens = _tokens(" ".join([skill.name, skill.description, *skill.tags]))

    overlap = len(intent_tokens & skill_tokens)
    coverage = overlap / max(len(skill_tokens), 1)

    host_supported = any(host in skill.hosts for host in host_targets)
    host_bonus = 0.15 if host_supported else -1.0

    evidence_bonus = 0.1 if (intent.evidence_level == "strict" and "quality" in skill.tags) else 0.0
    risk_bonus = 0.15 if (intent.risk_tier == "high" and "risk" in skill.tags) else 0.0
    preferred_source_bonus = (
        policy.preferred_source_bonus if skill.source_repo in set(policy.preferred_sources) else 0.0
    )

    utility = _is_utility_skill(skill, policy)
    explicit = _explicitly_requested(intent, skill, policy)
    utility_penalty = policy.utility_penalty if (utility and not explicit) else 0.0

    score = coverage + host_bonus + evidence_bonus + risk_bonus + preferred_source_bonus - utility_penalty
    reason_parts = []
    if overlap:
        reason_parts.append(f"matched {overlap} intent terms")
    if host_supported:
        reason_parts.append("host-compatible")
    if evidence_bonus:
        reason_parts.append("strict-evidence support")
    if risk_bonus:
        reason_parts.append("high-risk support")
    if utility and not explicit:
        reason_parts.append("utility penalty")
    if utility and explicit:
        reason_parts.append("explicitly requested")
    if preferred_source_bonus:
        reason_parts.append("preferred source")
    reason = ", ".join(reason_parts) if reason_parts else "fallback match"
    return SkillScore(skill=skill, score=score, reason=reason, utility=utility, explicitly_requested=explicit)


def _dependency_closure(selected: Dict[str, SkillScore], skills_by_id: Dict[str, SkillMetadata]) -> Dict[str, SkillScore]:
    queue = list(selected.keys())
    while queue:
        current_id = queue.pop(0)
        skill = skills_by_id.get(current_id)
        if not skill:
            continue
        for dep_id in skill.dependencies:
            if dep_id in selected:
                continue
            dep_skill = skills_by_id.get(dep_id)
            if dep_skill:
                selected[dep_id] = SkillScore(skill=dep_skill, score=0.0, reason=f"dependency of {current_id}")
                queue.append(dep_id)
    return selected


def _resolve_conflicts(selected: Dict[str, SkillScore]) -> Tuple[Dict[str, SkillScore], List[SkillReason]]:
    rejected: List[SkillReason] = []
    active_ids = set(selected.keys())

    for skill_id in list(selected.keys()):
        skill = selected[skill_id].skill
        for conflict_id in skill.conflicts:
            if conflict_id in active_ids and conflict_id in selected:
                current = selected[skill_id]
                conflict = selected[conflict_id]
                # deterministic conflict winner: higher score, then lexicographic ID
                keep_current = (current.score, skill_id) >= (conflict.score, conflict_id)
                drop_id = conflict_id if keep_current else skill_id
                if drop_id in selected:
                    rejected.append(SkillReason(skill_id=drop_id, reason=f"conflicts with {skill_id if drop_id==conflict_id else conflict_id}"))
                    del selected[drop_id]
                    active_ids.discard(drop_id)

    return selected, rejected


def _build_plan_payload(intent: BriefIntent, selected: List[SkillReason]) -> Dict[str, object]:
    tasks_by_phase = defaultdict(list)

    for skill in selected:
        sid = skill.skill_id
        if "orchestrator" in sid:
            tasks_by_phase["discovery"].append("Create project decomposition and ownership map")
            tasks_by_phase["ship"].append("Prepare closure checklist and retrospective")
        elif "research" in sid:
            tasks_by_phase["discovery"].append("Generate assumptions-vs-facts brief")
        elif "quality" in sid:
            tasks_by_phase["verify"].append("Run quality gate and risk challenge")
        elif "digital_product" in sid:
            tasks_by_phase["build"].append("Produce implementation backlog and execution plan")
            tasks_by_phase["ship"].append("Prepare release and handoff notes")
        else:
            tasks_by_phase["build"].append(f"Execute tasks using skill: {sid}")

    return {
        "intent": {
            "risk_tier": intent.risk_tier,
            "evidence_level": intent.evidence_level,
            "goals": intent.goals,
            "constraints": intent.constraints,
            "deliverables": intent.deliverables,
        },
        "phases": [
            {"name": phase, "tasks": tasks}
            for phase, tasks in [
                ("discovery", tasks_by_phase["discovery"]),
                ("build", tasks_by_phase["build"]),
                ("verify", tasks_by_phase["verify"]),
                ("ship", tasks_by_phase["ship"]),
            ]
            if tasks
        ],
    }


def route_skills(
    intent: BriefIntent,
    catalog: Sequence[SkillMetadata],
    host_targets: Sequence[str],
    policy: RoutingPolicy,
    snapshot_hash: str,
) -> RouteResult:
    skills_by_id = {skill.skill_id: skill for skill in catalog}
    scored = [_score_skill(intent, skill, host_targets, policy) for skill in catalog]
    scored.sort(key=lambda item: (-item.score, item.skill.skill_id))

    selected: Dict[str, SkillScore] = {}
    rejected: List[SkillReason] = []
    cluster_counts: Dict[str, int] = defaultdict(int)
    utility_count = 0

    for candidate in scored:
        skill_id = candidate.skill.skill_id

        if _is_excluded_skill(candidate.skill, policy):
            rejected.append(SkillReason(skill_id=skill_id, reason="excluded by policy"))
            continue

        if len(selected) >= policy.max_active_skills:
            rejected.append(SkillReason(skill_id=skill_id, reason="policy max_active_skills exceeded"))
            continue

        if not any(host in candidate.skill.hosts for host in host_targets):
            rejected.append(SkillReason(skill_id=skill_id, reason="host incompatibility"))
            continue

        if candidate.score < policy.min_relevance_score:
            rejected.append(SkillReason(skill_id=skill_id, reason="below relevance threshold"))
            continue

        cluster = skill_id.split(".", 1)[0]
        if cluster_counts[cluster] >= policy.max_skills_per_cluster:
            rejected.append(SkillReason(skill_id=skill_id, reason=f"cluster cap exceeded: {cluster}"))
            continue

        if candidate.utility:
            if utility_count >= policy.max_utility_skills:
                rejected.append(SkillReason(skill_id=skill_id, reason="utility skill cap exceeded"))
                continue
            utility_count += 1

        selected[skill_id] = candidate
        cluster_counts[cluster] += 1

    selected = _dependency_closure(selected, skills_by_id)
    selected, conflict_rejections = _resolve_conflicts(selected)
    rejected.extend(conflict_rejections)

    selected_reasons = [
        SkillReason(skill_id=selected[skill_id].skill.skill_id, reason=selected[skill_id].reason)
        for skill_id in sorted(selected)
    ]

    plan_payload = _build_plan_payload(intent, selected_reasons)
    plan_hash = sha256_hex(
        canonical_json(
            {
                "intent": intent.model_dump(),
                "selected": [item.model_dump() for item in selected_reasons],
                "snapshot_hash": snapshot_hash,
            }
        )
    )

    return RouteResult(
        route_id=str(uuid4()),
        plan_hash=plan_hash,
        selected_skills=selected_reasons,
        rejected_skills=rejected,
        snapshot_hash=snapshot_hash,
        plan_payload=plan_payload,
    )
