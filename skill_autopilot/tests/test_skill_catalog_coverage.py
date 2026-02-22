from __future__ import annotations

from pathlib import Path

from skill_autopilot.catalog import load_catalog
from skill_autopilot.config import CatalogSource


def test_packaged_catalog_has_broad_coverage() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    packaged_root = repo_root / "skill_autopilot" / "skills"
    skills, _ = load_catalog([CatalogSource(name="local_library", path=str(packaged_root), pinned_ref="test")])
    skill_ids = {item.skill_id for item in skills}

    # Guardrail so catalog breadth does not silently regress.
    assert len(skill_ids) >= 100

    required_prefixes = {
        "core",
        "discovery",
        "product",
        "architecture",
        "build",
        "qa",
        "data",
        "ai",
        "governance",
        "ops",
        "comms",
        "integration",
        "frontend",
        "backend",
        "mobile",
        "finance",
        "legal",
        "kernel",
    }
    for prefix in required_prefixes:
        assert any(skill_id.startswith(prefix + ".") for skill_id in skill_ids), prefix


def test_repo_and_packaged_skill_catalogs_are_mirrored() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    repo_catalog = repo_root / "library" / "skills"
    packaged_catalog = repo_root / "skill_autopilot" / "skills"

    repo_files = sorted(path.relative_to(repo_catalog) for path in repo_catalog.rglob("SKILL.md"))
    packaged_files = sorted(path.relative_to(packaged_catalog) for path in packaged_catalog.rglob("SKILL.md"))
    assert repo_files == packaged_files

    for rel in repo_files:
        left = (repo_catalog / rel).read_text(encoding="utf-8")
        right = (packaged_catalog / rel).read_text(encoding="utf-8")
        assert left == right, str(rel)

