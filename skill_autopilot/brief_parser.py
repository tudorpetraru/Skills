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

    return {k: _extract_bullets(v) for k, v in sections.items()}


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
        # fallback to first bullets in file as implied goals
        sections["goals"] = _extract_bullets(text.splitlines())[:5]

    try:
        intent = BriefIntent(
            goals=sections["goals"],
            constraints=sections["constraints"],
            deliverables=sections["deliverables"],
            risk_tier=_infer_risk(text),
            evidence_level=_infer_evidence(text),
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
