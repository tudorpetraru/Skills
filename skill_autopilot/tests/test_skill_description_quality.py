from __future__ import annotations

from pathlib import Path


REQUIRED_SECTIONS = [
    "## Job Mission",
    "## Scope and Responsibilities",
    "## Activation Signals",
    "## Required Inputs",
    "## Working Contract",
    "## Execution Workflow",
    "## Deliverables",
    "## Definition of Done",
    "## Guardrails",
    "## Collaboration and Handoff",
]


def test_all_skills_have_non_stub_job_descriptions() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    catalog = repo_root / "library" / "skills"
    skill_files = sorted(catalog.rglob("SKILL.md"))
    assert len(skill_files) >= 100

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        # Prevent regressions back to stubs.
        assert len(text) >= 1800, str(skill_file)
        for section in REQUIRED_SECTIONS:
            assert section in text, f"{skill_file} missing {section}"

