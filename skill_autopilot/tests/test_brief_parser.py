from __future__ import annotations

from pathlib import Path

from skill_autopilot.brief_parser import parse_brief, validate_brief_path


def _write_valid_brief(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# Goals",
                "- Build an AI financial advisor assistant with clear safety checks.",
                "- Keep implementation auditable and deterministic for enterprise usage.",
            ]
        ),
        encoding="utf-8",
    )


def test_parse_brief_accepts_quoted_path(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_valid_brief(brief)
    intent, _ = parse_brief(f"  '{brief}'  ")
    assert intent.goals


def test_parse_brief_accepts_file_uri(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_valid_brief(brief)
    intent, _ = parse_brief(brief.as_uri())
    assert intent.goals


def test_validate_brief_path_accepts_workspace_directory(tmp_path: Path) -> None:
    brief = tmp_path / "project_brief.md"
    _write_valid_brief(brief)
    result = validate_brief_path(str(tmp_path))
    assert result["exists"] is True
    assert result["is_file"] is True
    assert result["readable"] is True


def test_parse_brief_supports_env_path_mapping(tmp_path: Path, monkeypatch) -> None:
    mount_root = tmp_path / "host_mount"
    workspace = mount_root / "Bloomberg"
    workspace.mkdir(parents=True)
    brief = workspace / "project_brief.md"
    _write_valid_brief(brief)

    vm_path = "/sessions/demo/mnt/Bloomberg/project_brief.md"
    monkeypatch.setenv("SKILL_AUTOPILOT_PATH_MAPS", f"/sessions/demo/mnt={mount_root}")
    intent, _ = parse_brief(vm_path)
    assert intent.goals

    diag = validate_brief_path(vm_path)
    assert diag["resolution_mode"] == "mapped_cross_environment"
    assert diag["exists"] is True
