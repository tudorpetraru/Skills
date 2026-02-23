from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .config import CatalogSource
from .models import SkillMetadata
from .utils import canonical_json, sha256_hex


BUILTIN_SKILLS: List[SkillMetadata] = [
    SkillMetadata(
        skill_id="core.orchestrator",
        name="Orchestrator",
        description="Decomposes work and coordinates execution flow.",
        tags=["planning", "coordination", "delivery"],
        source_repo="builtin",
        pinned_ref="builtin-v1",
    ),
    SkillMetadata(
        skill_id="core.research",
        name="Research",
        description="Builds evidence-backed options and facts ledger.",
        tags=["research", "analysis", "evidence"],
        source_repo="builtin",
        pinned_ref="builtin-v1",
    ),
    SkillMetadata(
        skill_id="core.quality",
        name="Quality",
        description="Challenges assumptions, catches gaps, and validates acceptance criteria.",
        tags=["quality", "review", "risk"],
        source_repo="builtin",
        pinned_ref="builtin-v1",
    ),
    SkillMetadata(
        skill_id="kernel.digital_product",
        name="Digital Product Kernel",
        description="Build/ship workflows for software products with iterative delivery.",
        tags=["software", "product", "build", "ship"],
        dependencies=["core.orchestrator", "core.quality"],
        source_repo="builtin",
        pinned_ref="builtin-v1",
    ),
]


def _split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_frontmatter(text: str) -> Dict[str, object]:
    parsed: Dict[str, object] = {}
    if not text.startswith("---\n"):
        return parsed

    end = text.find("\n---\n", 4)
    if end == -1:
        return parsed

    block = text[4:end]
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = [item.strip() for item in line.split(":", 1)]
        if value.startswith("[") and value.endswith("]"):
            parsed[key.lower()] = _split_csv(value.strip("[]"))
        else:
            parsed[key.lower()] = value.strip('"').strip("'")

    return parsed


def _parse_inline_meta(text: str) -> Dict[str, List[str]]:
    # Optional metadata lines supported in SKILL.md body:
    # Hosts: claude_desktop,codex_desktop
    # Tags: planning,quality
    # Depends-On: skill_a,skill_b
    # Conflicts-With: skill_x
    meta: Dict[str, List[str]] = {
        "hosts": [],
        "tags": [],
        "dependencies": [],
        "conflicts": [],
    }

    patterns = {
        "hosts": r"^Hosts:\s*(.+)$",
        "tags": r"^Tags:\s*(.+)$",
        "dependencies": r"^Depends-On:\s*(.+)$",
        "conflicts": r"^Conflicts-With:\s*(.+)$",
    }

    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            body = text[end + 5 :]

    for line in body.splitlines():
        stripped = line.strip()
        for key, pattern in patterns.items():
            match = re.search(pattern, stripped, flags=re.IGNORECASE)
            if match:
                meta[key].extend(_split_csv(match.group(1)))

    return meta


def _extract_name_description(text: str, path: Path, frontmatter: Dict[str, object]) -> Tuple[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = str(frontmatter.get("name", path.parent.name))
    desc = str(frontmatter.get("description", "Skill template"))

    for line in lines:
        if line.startswith("#"):
            name = line.lstrip("# ").strip() or name
            break

    if not frontmatter.get("description"):
        for line in lines:
            if line.startswith(("#", "---", "name:", "description:")):
                continue
            if len(line) > 15:
                desc = line
                break

    return name, desc


def _to_list(value: object) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return _split_csv(value)
    return []


def _skill_from_file(skill_path: Path, source: CatalogSource) -> SkillMetadata | None:
    try:
        text = skill_path.read_text(encoding="utf-8")
    except OSError:
        return None

    frontmatter = _parse_frontmatter(text)
    name, description = _extract_name_description(text, skill_path, frontmatter)
    meta = _parse_inline_meta(text)

    relative_id = str(skill_path.parent).replace(str(Path(source.path)), "").strip("/")
    skill_id = relative_id.replace("/", ".") if relative_id else skill_path.parent.name

    hosts = _to_list(frontmatter.get("hosts")) + meta["hosts"]
    tags = _to_list(frontmatter.get("tags")) + meta["tags"]
    dependencies = _to_list(frontmatter.get("dependencies")) + _to_list(frontmatter.get("depends_on")) + meta["dependencies"]
    conflicts = _to_list(frontmatter.get("conflicts")) + _to_list(frontmatter.get("conflicts_with")) + meta["conflicts"]

    hosts = hosts or ["claude_desktop"]
    # Filter to valid hosts only.
    valid_hosts = {"claude_desktop"}
    hosts = [h for h in hosts if h in valid_hosts] or ["claude_desktop"]
    tags = tags or [word.lower() for word in re.findall(r"[a-zA-Z0-9_]+", name)[:4]]

    try:
        return SkillMetadata(
            skill_id=skill_id,
            name=name,
            description=description,
            tags=sorted(set(tags)),
            hosts=sorted(set(hosts)),
            dependencies=sorted(set(dependencies)),
            conflicts=sorted(set(conflicts)),
            source_repo=source.name,
            pinned_ref=source.pinned_ref,
        )
    except Exception:
        return None


def load_catalog(sources: Iterable[CatalogSource]) -> Tuple[List[SkillMetadata], str]:
    resolved_sources = []
    for source in sources:
        root = Path(source.path).expanduser().resolve()
        resolved_sources.append((source, root))

    loaded: Dict[str, SkillMetadata] = {skill.skill_id: skill for skill in BUILTIN_SKILLS}

    for source, root in resolved_sources:
        if not root.exists() or not root.is_dir():
            continue
        for skill_file in root.rglob("SKILL.md"):
            # If this file is inside another configured source root, only load
            # it via that more specific source to avoid duplicate IDs.
            skill_file_resolved = skill_file.resolve()
            if any(
                other_root != root
                and _path_is_relative_to(other_root, root)
                and _path_is_relative_to(skill_file_resolved, other_root)
                for _, other_root in resolved_sources
            ):
                continue
            skill = _skill_from_file(skill_file, source)
            if skill:
                loaded[skill.skill_id] = skill

    skills = sorted(loaded.values(), key=lambda skill: skill.skill_id)
    snapshot_hash = sha256_hex(canonical_json([skill.model_dump() for skill in skills]))
    return skills, snapshot_hash


def _path_is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
