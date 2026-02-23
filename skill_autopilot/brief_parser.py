from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import unquote, urlparse

from .models import BriefIntent
from .utils import canonical_json, sha256_hex


_SECTION_PATTERNS = {
    "goals": [r"^#+\s*goals?", r"^#+\s*objectives?", r"^#+\s*outcomes?"],
    "constraints": [r"^#+\s*constraints?", r"^#+\s*limits?", r"^#+\s*boundaries?"],
    "deliverables": [r"^#+\s*deliverables?", r"^#+\s*outputs?", r"^#+\s*artifacts?"],
}


class BriefValidationError(ValueError):
    pass


def _extract_bullets(lines: List[str]) -> List[str]:
    bullets: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            bullets.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            bullets.append(re.sub(r"^\d+\.\s+", "", stripped))
    return [b for b in bullets if b]


def _extract_candidates(lines: List[str], max_items: int = 8) -> List[str]:
    bullets = _extract_bullets(lines)
    if bullets:
        return bullets[:max_items]

    items: List[str] = []
    for raw in lines:
        text = raw.strip()
        if not text:
            continue
        if text.startswith("#"):
            continue
        if text.startswith("|") and text.endswith("|"):
            continue
        if re.match(r"^\d+\.\s+\[.+\]\(.+\)$", text):
            # table-of-contents style line
            continue

        normalized = re.sub(r"\s+", " ", text)
        parts = [p.strip(" -\t") for p in re.split(r"[.;]\s+", normalized) if p.strip()]
        for part in parts:
            if len(part) < 12:
                continue
            if part.lower().startswith("version:") or part.lower().startswith("date:"):
                continue
            items.append(part)
            if len(items) >= max_items:
                return items
    return items


def _extract_semantic_candidates(text: str, section: str, max_items: int = 8) -> List[str]:
    patterns = {
        "constraints": [
            r"\bmust\b",
            r"\bshould\b",
            r"\brequired\b",
            r"\bcannot\b",
            r"\bmust not\b",
            r"\bonly\b",
            r"\blimit(?:ed|s)?\b",
            r"\bbound(?:ed|s)?\b",
            r"\boffline\b",
            r"\bdeterministic\b",
            r"\blocal(?:-first)?\b",
        ],
        "deliverables": [
            r"\bdeliverable(?:s)?\b",
            r"\bartifact(?:s)?\b",
            r"\boutput(?:s)?\b",
            r"\bsummary\b",
            r"\breport\b",
            r"\bdocument(?:ation)?\b",
            r"\bplan\b",
            r"\bapp\b",
            r"\bservice\b",
            r"\bapi\b",
            r"\btool(?:s)?\b",
            r"\bpack(?:age|ager)?\b",
        ],
    }
    clues = patterns.get(section, [])
    if not clues:
        return []

    out: List[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if re.match(r"^\d+\.\s+\[.+\]\(.+\)\s*$", line):
            continue
        if line.startswith("|") and line.endswith("|"):
            continue
        if len(line) < 12:
            continue
        lowered = line.lower()
        if any(re.search(pattern, lowered) for pattern in clues):
            normalized = re.sub(r"\s+", " ", line).strip(" -\t")
            if normalized and normalized not in seen:
                seen.add(normalized)
                out.append(normalized)
                if len(out) >= max_items:
                    break
    return out


def _collect_sections(text: str) -> Dict[str, List[str]]:
    lines = text.splitlines()
    sections = {"goals": [], "constraints": [], "deliverables": []}
    current: str | None = None

    for line in lines:
        stripped = line.strip()
        matched_section = None
        for name, patterns in _SECTION_PATTERNS.items():
            if any(re.search(pattern, stripped, flags=re.IGNORECASE) for pattern in patterns):
                matched_section = name
                break
        if matched_section:
            current = matched_section
            continue

        if current and stripped:
            sections[current].append(stripped)

    return {k: _extract_candidates(v) for k, v in sections.items()}


def _infer_risk(text: str) -> str:
    low_terms = ["prototype", "demo", "internal only"]
    high_terms = ["regulated", "safety", "compliance", "financial controls", "medical"]
    lowered = text.lower()

    if any(term in lowered for term in high_terms):
        return "high"
    if any(term in lowered for term in low_terms):
        return "low"
    return "medium"


def _infer_evidence(text: str) -> str:
    strict_terms = ["audit", "traceability", "evidence", "change control", "approval"]
    lowered = text.lower()
    if sum(term in lowered for term in strict_terms) >= 2:
        return "strict"
    return "standard"


def _infer_project_type(text: str) -> str:
    """Detect the shape of work from the brief text."""
    lowered = text.lower()
    _TYPE_SIGNALS: List[tuple[str, list[str]]] = [
        ("new_build", ["greenfield", "new product", "new service", "build from scratch", "new platform"]),
        ("migration", ["migration", "migrate", "replatform", "lift and shift"]),
        ("integration", ["integration", "integrate", "connector", "api integration"]),
        ("refactor", ["refactor", "modernize", "re-architect", "tech debt"]),
        ("automation", ["automate", "automation", "workflow", "orchestrat"]),
        ("analysis", ["analysis", "research", "assessment", "evaluation", "audit"]),
    ]
    for ptype, signals in _TYPE_SIGNALS:
        if any(sig in lowered for sig in signals):
            return ptype
    return "general"


def _extract_pod_hints(text: str) -> List[str]:
    """Extract explicit pod/capability-area hints from the brief."""
    lowered = text.lower()
    hints: List[str] = []
    _POD_HINT_SIGNALS: List[tuple[str, list[str]]] = [
        ("commercial", ["go-to-market", "pricing strategy", "sales enablement"]),
        ("finance_governance", ["budget", "financial governance", "cost control", "sox compliance"]),
        ("legal_risk", ["legal review", "regulatory", "compliance requirement", "gdpr", "hipaa"]),
        ("people_talent", ["hiring plan", "onboarding", "team composition", "skill gap"]),
        ("ops_supply", ["procurement", "supply chain", "vendor management"]),
        ("data_insight", ["data pipeline", "bi report", "analytics dashboard"]),
    ]
    for pod_id, signals in _POD_HINT_SIGNALS:
        if any(sig in lowered for sig in signals):
            hints.append(pod_id)
    return hints


def parse_brief(brief_path: str) -> Tuple[BriefIntent, str]:
    if not str(brief_path).strip():
        raise BriefValidationError("brief_path is required")
    path, _, _ = _resolve_brief_path_details(brief_path)
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise BriefValidationError(f"Brief file not found: {path}") from exc
    except IsADirectoryError as exc:
        raise BriefValidationError(f"Brief path points to a directory, not a file: {path}") from exc
    except PermissionError as exc:
        raise BriefValidationError(
            f"Brief path is not readable due to permissions: {path}. "
            "Grant file access to this runtime or move the brief to an accessible folder."
        ) from exc
    except OSError as exc:
        raise BriefValidationError(f"Unable to read brief path: {path}. Error: {exc}") from exc

    if not text:
        raise BriefValidationError("project_brief.md is empty")

    sections = _collect_sections(text)
    if not sections["goals"]:
        # fallback to first meaningful lines in file as implied goals
        sections["goals"] = _extract_candidates(text.splitlines(), max_items=5)
    if not sections["constraints"]:
        sections["constraints"] = _extract_semantic_candidates(text, section="constraints", max_items=5)
    if not sections["deliverables"]:
        sections["deliverables"] = _extract_semantic_candidates(text, section="deliverables", max_items=5)

    from .pods import detect_industry

    industry = detect_industry(text)
    project_type = _infer_project_type(text)
    pod_hints = _extract_pod_hints(text)

    try:
        intent = BriefIntent(
            goals=sections["goals"],
            constraints=sections["constraints"],
            deliverables=sections["deliverables"],
            risk_tier=_infer_risk(text),
            evidence_level=_infer_evidence(text),
            industry=industry,
            project_type=project_type,
            pod_hints=pod_hints,
            raw_text=text,
        )
    except ValueError as exc:
        raise BriefValidationError(str(exc)) from exc

    intent_hash = sha256_hex(canonical_json(intent.model_dump()))
    return intent, intent_hash


def validate_brief_path(brief_path: str) -> Dict[str, object]:
    normalized = _normalize_path_input(brief_path)
    path, resolution_mode, resolution_note = _resolve_brief_path_details(brief_path)
    out: Dict[str, object] = {
        "input_path": brief_path,
        "normalized_input_path": normalized,
        "resolved_path": str(path),
        "resolution_mode": resolution_mode,
        "resolution_note": resolution_note,
        "exists": False,
        "is_file": False,
        "readable": False,
        "size_bytes": None,
        "error": None,
    }
    try:
        out["exists"] = path.exists()
        out["is_file"] = path.is_file()
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            out["readable"] = True
            out["size_bytes"] = len(text.encode("utf-8"))
        else:
            out["error"] = "Path is not a file"
    except PermissionError as exc:
        out["error"] = f"PermissionError: {exc}"
    except OSError as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def resolve_workspace_path(workspace_path: str) -> Dict[str, object]:
    normalized = _normalize_path_input(workspace_path)
    path = Path(normalized).expanduser()
    out: Dict[str, object] = {
        "input_path": workspace_path,
        "normalized_input_path": normalized,
        "resolved_path": str(path),
        "resolution_mode": "unresolved",
        "resolution_note": "path does not exist in MCP host filesystem",
        "exists": False,
        "is_dir": False,
        "error": None,
    }

    if path.exists():
        out.update(
            {
                "resolved_path": str(path),
                "resolution_mode": "direct",
                "resolution_note": "native path exists",
                "exists": True,
                "is_dir": path.is_dir(),
            }
        )
        return out

    sibling = _find_case_insensitive_sibling(path)
    if sibling is not None and sibling.exists():
        out.update(
            {
                "resolved_path": str(sibling),
                "resolution_mode": "case_insensitive_sibling",
                "resolution_note": "resolved by case-insensitive match",
                "exists": True,
                "is_dir": sibling.is_dir(),
            }
        )
        return out

    mapped = _map_cross_environment_path(path)
    if mapped is not None:
        mapped_path = mapped
        if mapped_path.exists():
            out.update(
                {
                    "resolved_path": str(mapped_path),
                    "resolution_mode": "mapped_cross_environment",
                    "resolution_note": f"mapped from {path}",
                    "exists": True,
                    "is_dir": mapped_path.is_dir(),
                }
            )
            return out
        mapped_sibling = _find_case_insensitive_sibling(mapped_path)
        if mapped_sibling is not None and mapped_sibling.exists():
            out.update(
                {
                    "resolved_path": str(mapped_sibling),
                    "resolution_mode": "mapped_cross_environment",
                    "resolution_note": f"mapped from {path} with case-insensitive match",
                    "exists": True,
                    "is_dir": mapped_sibling.is_dir(),
                }
            )
            return out

    return out


def _resolve_brief_path(brief_path: str) -> Path:
    return _resolve_brief_path_details(brief_path)[0]


def _resolve_brief_path_details(brief_path: str) -> Tuple[Path, str, str]:
    path = Path(_normalize_path_input(brief_path)).expanduser()
    if path.is_dir():
        path = path / "project_brief.md"
    if path.exists():
        return path, "direct", "native path exists"

    sibling = _find_case_insensitive_sibling(path)
    if sibling is not None:
        return sibling, "case_insensitive_sibling", "resolved by case-insensitive filename match"

    mapped = _map_cross_environment_path(path)
    if mapped is not None:
        mapped_path = mapped
        if mapped_path.is_dir():
            mapped_path = mapped_path / "project_brief.md"
        if mapped_path.exists():
            return mapped_path, "mapped_cross_environment", f"mapped from {path}"
        mapped_sibling = _find_case_insensitive_sibling(mapped_path)
        if mapped_sibling is not None:
            return mapped_sibling, "mapped_cross_environment", f"mapped from {path} with case-insensitive match"

    return path, "unresolved", "path does not exist in MCP host filesystem"


def _normalize_path_input(brief_path: str) -> str:
    cleaned = str(brief_path).strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        cleaned = cleaned[1:-1].strip()
    if cleaned.startswith("file://"):
        parsed = urlparse(cleaned)
        if parsed.scheme == "file":
            decoded = unquote(parsed.path or "")
            if parsed.netloc and parsed.netloc != "localhost":
                decoded = f"//{parsed.netloc}{decoded}"
            if decoded:
                cleaned = decoded
    return cleaned


def _find_case_insensitive_sibling(path: Path) -> Path | None:
    parent = path.parent
    if parent.exists() and parent.is_dir():
        target = path.name.lower()
        for child in parent.iterdir():
            if child.name.lower() == target:
                return child
    return None


def _map_cross_environment_path(path: Path) -> Path | None:
    from_env = _map_using_env_aliases(path)
    if from_env is not None:
        return from_env
    return _map_from_vm_mount(path)


def _map_using_env_aliases(path: Path) -> Path | None:
    # Format: SKILL_AUTOPILOT_PATH_MAPS="/sessions/abc/mnt=/Users/name/Documents/AI;/mnt=/Users/name/Documents"
    import os

    raw = os.getenv("SKILL_AUTOPILOT_PATH_MAPS", "").strip()
    if not raw:
        return None
    source_path = path.as_posix()
    for item in re.split(r"[;,]", raw):
        if "=" not in item:
            continue
        src, dst = item.split("=", 1)
        src = src.strip().rstrip("/")
        dst = dst.strip().rstrip("/")
        if not src or not dst:
            continue
        if source_path == src or source_path.startswith(src + "/"):
            suffix = source_path[len(src) :].lstrip("/")
            mapped = Path(dst)
            if suffix:
                mapped = mapped / suffix
            return mapped.expanduser()
    return None


def _map_from_vm_mount(path: Path) -> Path | None:
    as_posix = path.as_posix()
    if "/mnt/" not in as_posix:
        return None
    tail = as_posix.split("/mnt/", 1)[1].lstrip("/")
    if not tail:
        return None
    tail_path = Path(tail)

    home = Path.home()
    roots = [home / "Documents", home / "Desktop", home / "Downloads"]
    for root in roots:
        for prefix in ["", "AI", "Projects", "Workspaces"]:
            candidate = (root / prefix / tail_path) if prefix else (root / tail_path)
            if candidate.exists():
                return candidate

    # Fallback: bounded suffix search under common roots.
    filename = tail_path.name
    if not filename:
        return None
    suffix_parts = tail_path.parts
    for root in roots:
        if not root.exists():
            continue
        seen = 0
        for match in root.rglob(filename):
            seen += 1
            if seen > 500:
                break
            parts = match.parts
            if len(parts) >= len(suffix_parts) and tuple(parts[-len(suffix_parts) :]) == tuple(suffix_parts):
                return match
            if len(suffix_parts) >= 2 and len(parts) >= 2 and tuple(parts[-2:]) == tuple(suffix_parts[-2:]):
                return match
    return None


def is_material_change(previous_intent: BriefIntent, new_intent: BriefIntent) -> bool:
    if previous_intent.risk_tier != new_intent.risk_tier:
        return True
    if previous_intent.evidence_level != new_intent.evidence_level:
        return True

    old_tokens = set(re.findall(r"[a-zA-Z0-9_]+", previous_intent.raw_text.lower()))
    new_tokens = set(re.findall(r"[a-zA-Z0-9_]+", new_intent.raw_text.lower()))
    if not old_tokens and not new_tokens:
        return False

    overlap = len(old_tokens & new_tokens)
    union = len(old_tokens | new_tokens) or 1
    jaccard = overlap / union
    return jaccard < 0.95
