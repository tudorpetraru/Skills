from __future__ import annotations

from typing import Dict, List, Sequence
from uuid import uuid4

from .models import BriefIntent, SkillReason


def decompose_project(intent: BriefIntent, selected_skills: Sequence[SkillReason]) -> Dict[str, object]:
    role_map = {
        "orchestrator": "orchestrator",
        "research": "research",
        "quality": "quality",
        "digital_product": "delivery",
    }

    phases: List[Dict[str, object]] = []
    phase_specs = [
        ("discovery", ["Clarify goals, constraints, and risks", "Confirm acceptance criteria"]),
        ("build", ["Execute planned tasks with selected skills"]),
        ("verify", ["Run quality checks and resolve issues"]),
        ("ship", ["Finalize deliverables and closure summary"]),
    ]

    for name, base_tasks in phase_specs:
        tasks: List[Dict[str, object]] = []
        for index, base in enumerate(base_tasks, start=1):
            tasks.append(
                {
                    "task_id": f"{name}-{index}",
                    "title": base,
                    "inputs": ["project_brief.md"],
                    "outputs": ["phase_notes.md"],
                    "acceptance_checks": ["Task completed with evidence"],
                    "escalation_trigger": ["Blocked > 1 day"],
                }
            )

        for skill in selected_skills:
            sid = skill.skill_id
            role = "delivery"
            for key, candidate_role in role_map.items():
                if key in sid:
                    role = candidate_role
                    break
            tasks.append(
                {
                    "task_id": f"{name}-{sid}",
                    "title": f"Apply {sid} for {name}",
                    "inputs": ["intent", "selected_skill"],
                    "outputs": ["task_output"],
                    "agent_role": role,
                    "acceptance_checks": ["Output aligned with project goals"],
                    "escalation_trigger": ["Missing required input"],
                }
            )

        phases.append({"name": name, "tasks": tasks})

    return {
        "action_plan_id": str(uuid4()),
        "summary": {
            "risk_tier": intent.risk_tier,
            "evidence_level": intent.evidence_level,
            "goal_count": len(intent.goals),
            "constraint_count": len(intent.constraints),
            "deliverable_count": len(intent.deliverables),
        },
        "phases": phases,
        "gates": [
            {"gate_id": "gate-1", "criteria": ["Discovery reviewed"], "owner": "orchestrator"},
            {"gate_id": "gate-2", "criteria": ["Quality checks complete"], "owner": "quality"},
        ],
    }
