from __future__ import annotations

import os
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        tomllib = None  # type: ignore
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


DEFAULT_HOME = Path.home() / ".project-skill-router"
DEFAULT_CONFIG_PATH = DEFAULT_HOME / "config.toml"
DEFAULT_DB_PATH = DEFAULT_HOME / "state.db"
DEFAULT_SERVICE_URL = "http://127.0.0.1:8787"


@dataclass
class CatalogSource:
    name: str
    path: str
    pinned_ref: str = "local"


@dataclass
class AppConfig:
    service_host: str = "127.0.0.1"
    service_port: int = 8787
    db_path: str = str(DEFAULT_DB_PATH)
    lease_ttl_hours: int = 24
    max_active_skills: int = 12
    min_relevance_score: float = 0.22
    max_utility_skills: int = 1
    max_skills_per_cluster: int = 4
    utility_penalty: float = 0.35
    preferred_sources: List[str] = field(default_factory=lambda: ["local_library"])
    preferred_source_bonus: float = 0.08
    adapter_mode: str = "native_cli"
    worker_pool_size: int = 6
    role_host_map: Dict[str, str] = field(
        default_factory=lambda: {
            "orchestrator": "claude_desktop",
            "research": "claude_desktop",
            "quality": "codex_desktop",
            "delivery": "codex_desktop",
        }
    )
    remote_worker_endpoints: List[str] = field(default_factory=list)
    admin_mode: bool = False
    allowlisted_catalogs: List[CatalogSource] = field(default_factory=list)


def ensure_default_config(config_path: Path = DEFAULT_CONFIG_PATH) -> Path:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        return config_path

    default_catalogs = [
        CatalogSource(name="local_library", path=str(Path.cwd() / "library" / "skills"), pinned_ref="local-v1"),
        CatalogSource(name="codex_home_skills", path=str(Path.home() / ".codex" / "skills"), pinned_ref="local"),
        CatalogSource(name="workspace_skills", path=str(Path.cwd()), pinned_ref="workspace"),
    ]

    lines = [
        '[service]',
        'host = "127.0.0.1"',
        'port = 8787',
        '',
        '[policy]',
        f'db_path = "{DEFAULT_DB_PATH}"',
        'lease_ttl_hours = 24',
        'max_active_skills = 12',
        'min_relevance_score = 0.22',
        'max_utility_skills = 1',
        'max_skills_per_cluster = 4',
        'utility_penalty = 0.35',
        'preferred_sources = "local_library"',
        'preferred_source_bonus = 0.08',
        'adapter_mode = "native_cli"',
        'worker_pool_size = 6',
        'role_host_map = "orchestrator:claude_desktop,research:claude_desktop,quality:codex_desktop,delivery:codex_desktop"',
        'remote_worker_endpoints = ""',
        'admin_mode = false',
        '',
    ]

    for catalog in default_catalogs:
        lines.extend(
            [
                '[[catalogs]]',
                f'name = "{catalog.name}"',
                f'path = "{catalog.path}"',
                f'pinned_ref = "{catalog.pinned_ref}"',
                '',
            ]
        )

    config_path.write_text("\n".join(lines), encoding="utf-8")
    return config_path


def load_config(config_path: Path | None = None) -> AppConfig:
    path = ensure_default_config(config_path or DEFAULT_CONFIG_PATH)
    text = path.read_text(encoding="utf-8")
    parsed = tomllib.loads(text) if tomllib is not None else _parse_minimal_toml(text)

    service = parsed.get("service", {})
    policy = parsed.get("policy", {})

    catalogs: List[CatalogSource] = []
    for item in parsed.get("catalogs", []):
        source = CatalogSource(
            name=item.get("name", "catalog"),
            path=item.get("path", ""),
            pinned_ref=item.get("pinned_ref", "local"),
        )
        if source.path:
            catalogs.append(source)

    if not catalogs:
        catalogs.append(CatalogSource(name="workspace_skills", path=str(Path.cwd()), pinned_ref="workspace"))

    return AppConfig(
        service_host=service.get("host", "127.0.0.1"),
        service_port=int(service.get("port", 8787)),
        db_path=policy.get("db_path", str(DEFAULT_DB_PATH)),
        lease_ttl_hours=int(policy.get("lease_ttl_hours", 24)),
        max_active_skills=int(policy.get("max_active_skills", 12)),
        min_relevance_score=float(policy.get("min_relevance_score", 0.22)),
        max_utility_skills=int(policy.get("max_utility_skills", 1)),
        max_skills_per_cluster=int(policy.get("max_skills_per_cluster", 4)),
        utility_penalty=float(policy.get("utility_penalty", 0.35)),
        preferred_sources=_split_csv_str(policy.get("preferred_sources", "local_library")),
        preferred_source_bonus=float(policy.get("preferred_source_bonus", 0.08)),
        adapter_mode=str(policy.get("adapter_mode", "native_cli")),
        worker_pool_size=int(policy.get("worker_pool_size", 6)),
        role_host_map=_parse_role_host_map(policy.get("role_host_map", "orchestrator:claude_desktop,research:claude_desktop,quality:codex_desktop,delivery:codex_desktop")),
        remote_worker_endpoints=_split_csv_str(policy.get("remote_worker_endpoints", "")),
        admin_mode=bool(policy.get("admin_mode", False)),
        allowlisted_catalogs=catalogs,
    )


def service_url(config: AppConfig) -> str:
    return f"http://{config.service_host}:{config.service_port}"


def ensure_parent_dir(path: str) -> None:
    Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def _parse_minimal_toml(text: str) -> dict:
    """Fallback parser for this app's limited TOML shape."""
    parsed: dict = {"catalogs": []}
    current_section: str | None = None
    current_catalog: dict | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[service]":
            current_section = "service"
            parsed.setdefault("service", {})
            continue
        if line == "[policy]":
            current_section = "policy"
            parsed.setdefault("policy", {})
            continue
        if line == "[[catalogs]]":
            current_section = "catalogs"
            current_catalog = {}
            parsed["catalogs"].append(current_catalog)
            continue
        if "=" not in line:
            continue

        key, value = [item.strip() for item in line.split("=", 1)]
        if value.lower() in {"true", "false"}:
            parsed_value: object = value.lower() == "true"
        elif value.startswith('"') and value.endswith('"'):
            parsed_value = value.strip('"')
        else:
            try:
                parsed_value = int(value)
            except ValueError:
                try:
                    parsed_value = float(value)
                except ValueError:
                    parsed_value = value

        if current_section == "catalogs" and current_catalog is not None:
            current_catalog[key] = parsed_value
        elif current_section:
            parsed[current_section][key] = parsed_value

    return parsed


def _split_csv_str(value: object) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _parse_role_host_map(value: object) -> Dict[str, str]:
    items = _split_csv_str(value)
    mapping: Dict[str, str] = {}
    for item in items:
        if ":" not in item:
            continue
        role, host = item.split(":", 1)
        role = role.strip()
        host = host.strip()
        if role and host:
            mapping[role] = host
    if not mapping:
        return {
            "orchestrator": "claude_desktop",
            "research": "claude_desktop",
            "quality": "codex_desktop",
            "delivery": "codex_desktop",
        }
    return mapping
