from __future__ import annotations

from pathlib import Path

from skill_autopilot.config import load_config


def test_default_catalogs_include_packaged_library(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    cfg = load_config(config_path)
    sources = {item.name: item.path for item in cfg.allowlisted_catalogs}
    assert "local_library" in sources
    assert Path(sources["local_library"]).name == "skills"
    assert Path(sources["local_library"]).exists()
