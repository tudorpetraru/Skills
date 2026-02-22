from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .config import DEFAULT_CONFIG_PATH, ensure_default_config, load_config


@dataclass
class CheckResult:
    name: str
    ok: bool
    critical: bool
    detail: str


def _check_python() -> CheckResult:
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 11)
    return CheckResult(
        name="python_version",
        ok=ok,
        critical=True,
        detail=f"{v.major}.{v.minor}.{v.micro} (requires >=3.11)",
    )


def _check_cli(name: str, critical: bool = False) -> CheckResult:
    path = shutil.which(name)
    return CheckResult(
        name=f"cli:{name}",
        ok=path is not None,
        critical=critical,
        detail=path or "not found in PATH",
    )


def _check_config(config_path: Path) -> List[CheckResult]:
    results: List[CheckResult] = []
    try:
        resolved = ensure_default_config(config_path)
        results.append(CheckResult("config_exists", True, True, str(resolved)))
        text = resolved.read_text(encoding="utf-8")
        results.append(CheckResult("config_readable", bool(text.strip()), True, "readable"))
    except Exception as exc:
        results.append(CheckResult("config_exists", False, True, f"{type(exc).__name__}: {exc}"))
        return results

    try:
        cfg = load_config(config_path)
        catalog_paths = [str(Path(item.path).expanduser()) for item in cfg.allowlisted_catalogs]
        existing = [p for p in catalog_paths if Path(p).exists()]
        results.append(
            CheckResult(
                "catalog_sources",
                len(existing) > 0,
                True,
                f"configured={len(catalog_paths)}, existing={len(existing)}",
            )
        )
    except Exception as exc:
        results.append(CheckResult("catalog_sources", False, True, f"{type(exc).__name__}: {exc}"))

    return results


def _check_state_dirs(config_path: Path) -> List[CheckResult]:
    results: List[CheckResult] = []
    try:
        cfg = load_config(config_path)
        db_parent = Path(cfg.db_path).expanduser().parent
        db_parent.mkdir(parents=True, exist_ok=True)
        probe = db_parent / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        results.append(CheckResult("state_writable", True, True, str(db_parent)))
    except Exception as exc:
        results.append(CheckResult("state_writable", False, True, f"{type(exc).__name__}: {exc}"))
    return results


def _check_mcp_health() -> CheckResult:
    mcp_path = shutil.which("skill-autopilot-mcp")
    if not mcp_path:
        sibling = Path(sys.executable).resolve().parent / "skill-autopilot-mcp"
        if sibling.exists():
            mcp_path = str(sibling)
    if not mcp_path:
        return CheckResult("mcp_binary", False, True, "skill-autopilot-mcp not found in PATH")
    try:
        proc = subprocess.run(
            [mcp_path, "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception as exc:
        return CheckResult("mcp_binary", False, True, f"{type(exc).__name__}: {exc}")
    ok = proc.returncode == 0
    detail = mcp_path if ok else (proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}")
    return CheckResult("mcp_binary", ok, True, detail)


def run_doctor(config_path: Path) -> List[CheckResult]:
    results: List[CheckResult] = []
    results.append(_check_python())
    results.extend(_check_config(config_path))
    results.extend(_check_state_dirs(config_path))
    results.append(_check_mcp_health())
    results.append(_check_cli("claude", critical=False))
    results.append(_check_cli("codex", critical=False))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose local Skill Autopilot installation health")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config TOML")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any non-critical checks fail")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).expanduser()
    results = run_doctor(config_path)

    critical_failures = [item for item in results if item.critical and not item.ok]
    any_failures = [item for item in results if not item.ok]

    if args.json:
        payload = {
            "ok": len(critical_failures) == 0 and (len(any_failures) == 0 if args.strict else True),
            "checks": [
                {"name": item.name, "ok": item.ok, "critical": item.critical, "detail": item.detail}
                for item in results
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print("Skill Autopilot Doctor")
        for item in results:
            status = "OK" if item.ok else "FAIL"
            scope = "critical" if item.critical else "optional"
            print(f"- [{status}] {item.name} ({scope}) -> {item.detail}")

    if critical_failures:
        raise SystemExit(1)
    if args.strict and any_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
