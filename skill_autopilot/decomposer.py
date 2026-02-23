"""Pod-aware project decomposition.

Replaces the flat phase generation with a system that:
1. Always includes Core pod agents in the plan
2. Selects B-kernel(s) based on industry/project type
3. Attaches relevant pods based on brief analysis
4. Generates tasks where each task maps to a specific agent within a pod
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence
from uuid import uuid4

from .models import BriefIntent, PodAssignment, SkillReason, TaskInstruction, TaskState
from .pods import (
    CORE_POD,
    KernelSpec,
    PodSpec,
    select_kernels,
    select_pods,
)


def decompose_project(
    intent: BriefIntent,
    selected_skills: Sequence[SkillReason],
) -> Dict[str, object]:
    """Decompose a project into pod-aware phases and tasks.

    Returns the action plan dict stored in the database.
    """
    pods = select_pods(
        intent_text=intent.raw_text,
        industry=intent.industry,
        pod_hints=intent.pod_hints,
    )
    kernels = select_kernels(
        industry=intent.industry,
        intent_text=intent.raw_text,
    )

    # Build pod assignments for the plan metadata.
    pod_assignments: List[Dict[str, object]] = []
    for pod in pods.values():
        pod_assignments.append({
            "pod_id": pod.pod_id,
            "pod_name": pod.name,
            "agents": list(pod.agents),
            "always_on": pod.always_on,
        })
    for kernel in kernels:
        pod_assignments.append({
            "pod_id": f"kernel.{kernel.kernel_id}",
            "pod_name": kernel.name,
            "agents": [],
            "kernel_id": kernel.kernel_id,
            "always_on": False,
        })

    # Generate tasks per phase.
    phases = _generate_phases(intent, pods, kernels, selected_skills)

    return {
        "action_plan_id": str(uuid4()),
        "summary": {
            "risk_tier": intent.risk_tier,
            "evidence_level": intent.evidence_level,
            "industry": intent.industry,
            "project_type": intent.project_type,
            "goal_count": len(intent.goals),
            "constraint_count": len(intent.constraints),
            "deliverable_count": len(intent.deliverables),
            "kernel_count": len(kernels),
            "pod_count": len(pods),
        },
        "pods": pod_assignments,
        "kernels": [
            {
                "kernel_id": k.kernel_id,
                "name": k.name,
                "description": k.description,
            }
            for k in kernels
        ],
        "phases": phases,
        "gates": [
            {"gate_id": "gate-1", "criteria": ["Discovery reviewed and goals confirmed"], "owner": "orchestrator"},
            {"gate_id": "gate-2", "criteria": ["Quality checks complete, deliverables verified"], "owner": "quality"},
        ],
    }


def _generate_phases(
    intent: BriefIntent,
    pods: Dict[str, PodSpec],
    kernels: List[KernelSpec],
    selected_skills: Sequence[SkillReason],
) -> List[Dict[str, object]]:
    """Generate the four standard phases with pod-contextual tasks."""
    phases: List[Dict[str, object]] = []

    # --- Discovery phase ---
    discovery_tasks = _discovery_tasks(intent, pods, kernels)
    phases.append({"name": "discovery", "tasks": discovery_tasks})

    # --- Build phase ---
    build_tasks = _build_tasks(intent, pods, kernels, selected_skills)
    phases.append({"name": "build", "tasks": build_tasks})

    # --- Verify phase ---
    verify_tasks = _verify_tasks(intent, pods, kernels)
    phases.append({"name": "verify", "tasks": verify_tasks})

    # --- Ship phase ---
    ship_tasks = _ship_tasks(intent, pods)
    phases.append({"name": "ship", "tasks": ship_tasks})

    # Assign order indices.
    global_idx = 0
    for phase in phases:
        for task in phase["tasks"]:
            global_idx += 1
            task["order_index"] = global_idx

    return phases


def _discovery_tasks(
    intent: BriefIntent,
    pods: Dict[str, PodSpec],
    kernels: List[KernelSpec],
) -> List[Dict[str, object]]:
    tasks: List[Dict[str, object]] = []

    # Core orchestrator scopes the project.
    tasks.append(_make_task(
        task_id="discovery-scope",
        title="Scope the project: clarify goals, constraints, and acceptance criteria",
        phase="discovery",
        pod_id="core",
        agent="orchestrator",
        skill_id="core.orchestrator",
        instructions=(
            "Read the project brief and produce an objective snapshot.\n"
            "Define: what is in scope, what is out of scope, key success criteria, "
            "major constraints, and known risks.\n"
            "Output a clear, concise scope document."
        ),
        acceptance_criteria=[
            "Goals are specific and measurable",
            "Constraints listed with rationale",
            "Acceptance criteria defined for each deliverable",
        ],
        inputs=["project_brief.md"],
        outputs=["scope_document.md"],
    ))

    # Core research gathers context.
    tasks.append(_make_task(
        task_id="discovery-research",
        title="Research context: gather facts, compare options, and identify unknowns",
        phase="discovery",
        pod_id="core",
        agent="research",
        skill_id="core.research",
        instructions=(
            "Gather relevant background information for the project.\n"
            "Compare approaches, identify prior art, and flag open questions.\n"
            "Maintain a facts vs assumptions ledger."
        ),
        acceptance_criteria=[
            "Key facts documented with sources",
            "Assumptions explicitly listed",
            "Open questions flagged for resolution",
        ],
        inputs=["project_brief.md", "scope_document.md"],
        outputs=["research_briefing.md"],
    ))

    # Discovery pod tasks (if attached).
    if "discovery" in pods:
        tasks.append(_make_task(
            task_id="discovery-requirements",
            title="Specify requirements and define acceptance criteria",
            phase="discovery",
            pod_id="discovery",
            agent="requirements_specifier",
            skill_id="discovery.requirements_specifier",
            instructions=(
                "Convert high-level goals into specific, testable requirements.\n"
                "For each deliverable, define acceptance criteria and evidence needed."
            ),
            acceptance_criteria=[
                "Requirements are traceable to goals",
                "Each requirement has acceptance criteria",
            ],
            inputs=["scope_document.md", "research_briefing.md"],
            outputs=["requirements.md"],
        ))

    # Kernel-specific discovery.
    for kernel in kernels:
        tasks.append(_make_task(
            task_id=f"discovery-kernel-{kernel.kernel_id}",
            title=f"Assess {kernel.name} readiness and define kernel-specific approach",
            phase="discovery",
            pod_id=f"kernel.{kernel.kernel_id}",
            agent="kernel_assessor",
            skill_id=f"kernel.{kernel.kernel_id}",
            instructions=(
                f"Evaluate project readiness for {kernel.name} delivery.\n"
                f"Description: {kernel.description}\n"
                "Identify domain-specific standards, required artifacts, and evidence rules.\n"
                "Define the build approach and key decision points."
            ),
            acceptance_criteria=[
                f"{kernel.name} approach defined",
                "Domain standards identified",
                "Key decision points documented",
            ],
            inputs=["scope_document.md", "requirements.md"],
            outputs=[f"{kernel.kernel_id}_approach.md"],
        ))

    return tasks


def _build_tasks(
    intent: BriefIntent,
    pods: Dict[str, PodSpec],
    kernels: List[KernelSpec],
    selected_skills: Sequence[SkillReason],
) -> List[Dict[str, object]]:
    tasks: List[Dict[str, object]] = []

    # Core orchestrator creates execution plan.
    tasks.append(_make_task(
        task_id="build-plan",
        title="Create detailed execution plan with task graph and dependencies",
        phase="build",
        pod_id="core",
        agent="orchestrator",
        skill_id="core.orchestrator",
        instructions=(
            "Using discovery outputs, create a detailed execution plan.\n"
            "Define task graph with dependencies, owners, and acceptance gates.\n"
            "Identify parallelizable work and critical path.\n"
            "NOTE: This is the only planning-only task. All subsequent build tasks must produce real, working implementation files."
        ),
        acceptance_criteria=[
            "Task dependencies are explicit",
            "Each task has a clear owner (skill/agent)",
            "Critical path identified",
        ],
        inputs=["scope_document.md", "requirements.md"],
        outputs=["execution_plan.md"],
    ))

    # Kernel-specific build tasks.
    for kernel in kernels:
        tasks.append(_make_task(
            task_id=f"build-kernel-{kernel.kernel_id}",
            title=f"Execute {kernel.name} deliverables",
            phase="build",
            pod_id=f"kernel.{kernel.kernel_id}",
            agent="builder",
            skill_id=f"kernel.{kernel.kernel_id}",
            instructions=(
                f"Implement the actual deliverables for {kernel.name} — write real, working files.\n"
                f"Description: {kernel.description}\n"
                "Do NOT produce documentation about what to build; produce the actual artifacts.\n"
                "Read the execution plan and build the code, configs, schemas, or other concrete outputs it specifies.\n"
                "Save all outputs into the workspace directory."
            ),
            acceptance_criteria=[
                "Deliverables produced per execution plan",
                "Change control and traceability maintained",
                "Verification evidence collected",
            ],
            inputs=["execution_plan.md", f"{kernel.kernel_id}_approach.md"],
            outputs=[f"{kernel.kernel_id}_deliverables/"],
        ))

    # Skill-specific build tasks.
    for skill in selected_skills:
        sid = skill.skill_id
        # Skip skills already covered by core or kernel tasks.
        if sid.startswith("core.") or sid.startswith("kernel."):
            continue
        tasks.append(_make_task(
            task_id=f"build-skill-{sid}",
            title=f"Apply {sid}: {skill.reason}",
            phase="build",
            pod_id=_pod_id_from_skill(sid),
            agent=sid.split(".")[-1] if "." in sid else sid,
            skill_id=sid,
            instructions=(
                f"Implement the concrete outputs for {sid}.\n"
                f"Context: {skill.reason}\n"
                "Write real, working files \u2014 not documentation about what to write.\n"
                "Save outputs to the workspace directory alongside other project files."
            ),
            acceptance_criteria=["Output aligned with project goals"],
            inputs=["execution_plan.md"],
            outputs=[f"{sid}_output.md"],
        ))

    # Core scribe documents progress.
    tasks.append(_make_task(
        task_id="build-document",
        title="Document build progress and decisions",
        phase="build",
        pod_id="core",
        agent="scribe",
        skill_id="core.scribe",
        instructions=(
            "Document all decisions, changes, and progress during build phase.\n"
            "Maintain changelog and decision log.\n"
            "Produce build summary for stakeholders."
        ),
        acceptance_criteria=[
            "All major decisions documented with rationale",
            "Changelog is current",
        ],
        inputs=["execution_plan.md"],
        outputs=["build_summary.md", "decision_log.md"],
    ))

    return tasks


def _verify_tasks(
    intent: BriefIntent,
    pods: Dict[str, PodSpec],
    kernels: List[KernelSpec],
) -> List[Dict[str, object]]:
    tasks: List[Dict[str, object]] = []

    # Core quality runs checks.
    tasks.append(_make_task(
        task_id="verify-quality",
        title="Run quality checks: verify deliverables against acceptance criteria",
        phase="verify",
        pod_id="core",
        agent="quality",
        skill_id="core.quality",
        instructions=(
            "Review all deliverables against acceptance criteria.\n"
            "Actually inspect the produced files \u2014 open them, check they work, verify content.\n"
            "Run any test suites, linters, or validation scripts that exist.\n"
            "Produce a quality report with pass/fail status per deliverable."
        ),
        acceptance_criteria=[
            "Every deliverable reviewed against criteria",
            "Gaps and risks documented",
            "Quality report produced",
        ],
        inputs=["requirements.md", "build_summary.md"],
        outputs=["quality_report.md"],
    ))

    # Kernel-specific verification.
    for kernel in kernels:
        tasks.append(_make_task(
            task_id=f"verify-kernel-{kernel.kernel_id}",
            title=f"Verify {kernel.name} deliverables: domain-specific validation",
            phase="verify",
            pod_id=f"kernel.{kernel.kernel_id}",
            agent="verifier",
            skill_id=f"kernel.{kernel.kernel_id}",
            instructions=(
                f"Perform domain-specific verification for {kernel.name}.\n"
                f"Description: {kernel.description}\n"
                "Actually inspect the deliverable files and run validation checks.\n"
                "Check compliance with domain standards and evidence requirements.\n"
                "Validate that all readiness gates are satisfied."
            ),
            acceptance_criteria=[
                f"{kernel.name} standards compliance verified",
                "Readiness gates satisfied",
                "Evidence collected and traceable",
            ],
            inputs=[f"{kernel.kernel_id}_deliverables/", "quality_report.md"],
            outputs=[f"{kernel.kernel_id}_verification.md"],
        ))

    return tasks


def _ship_tasks(
    intent: BriefIntent,
    pods: Dict[str, PodSpec],
) -> List[Dict[str, object]]:
    tasks: List[Dict[str, object]] = []

    # Delivery tracker finalizes.
    tasks.append(_make_task(
        task_id="ship-finalize",
        title="Finalize deliverables and produce closure summary",
        phase="ship",
        pod_id="core",
        agent="delivery_tracker",
        skill_id="core.delivery_tracker",
        instructions=(
            "Compile all deliverables into a final package in the workspace.\n"
            "Verify all output files are present and correctly organized.\n"
            "Produce a closure summary listing: what was delivered (with file paths), "
            "what was deferred, lessons learned, and recommended next steps."
        ),
        acceptance_criteria=[
            "All planned deliverables accounted for",
            "Deferred items documented with rationale",
            "Closure summary produced",
        ],
        inputs=["quality_report.md", "build_summary.md"],
        outputs=["closure_summary.md"],
    ))

    # Scribe produces final documentation.
    tasks.append(_make_task(
        task_id="ship-docs",
        title="Produce final documentation and handoff package",
        phase="ship",
        pod_id="core",
        agent="scribe",
        skill_id="core.scribe",
        instructions=(
            "Compile final documentation package.\n"
            "Include: project summary, decision log, deliverable index, "
            "and any handoff notes for downstream owners."
        ),
        acceptance_criteria=[
            "Documentation is complete and indexed",
            "Handoff notes are actionable",
        ],
        inputs=["closure_summary.md", "decision_log.md"],
        outputs=["final_documentation/"],
    ))

    return tasks


def _make_task(
    task_id: str,
    title: str,
    phase: str,
    pod_id: str,
    agent: str,
    skill_id: str,
    instructions: str,
    acceptance_criteria: List[str],
    inputs: List[str],
    outputs: List[str],
) -> Dict[str, object]:
    """Create a task dict with full instruction context."""
    return {
        "task_id": task_id,
        "title": title,
        "phase": phase,
        "state": TaskState.PENDING.value,
        "pod_id": pod_id,
        "agent": agent,
        "skill_id": skill_id,
        "instructions": instructions,
        "acceptance_criteria": acceptance_criteria,
        "inputs": inputs,
        "outputs": outputs,
        "guardrails": [
            "Do not invent facts or metrics.",
            "State assumptions and confidence clearly.",
            "Prefer smallest viable scope that meets the objective.",
            "Save all output files to the workspace root directory, not in subdirectories, unless the task explicitly requires a directory structure.",
        ],
        "order_index": 0,
    }


def _pod_id_from_skill(skill_id: str) -> str:
    """Derive pod_id from a skill_id (e.g. 'architecture.system_designer' -> 'architecture')."""
    if "." in skill_id:
        return skill_id.split(".")[0]
    return "build"
