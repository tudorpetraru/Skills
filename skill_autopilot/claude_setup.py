from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


DEFAULT_CLAUDE_CONFIG = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"


def _resolve_mcp_command() -> str:
    path = shutil.which("skill-autopilot-mcp")
    if path:
        return path
    candidate = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "skill-autopilot-mcp"
    if candidate.exists():
        return str(candidate)
    raise RuntimeError("Could not locate skill-autopilot-mcp in PATH")


def _build_server_entry(command: str, transport: str) -> Dict[str, Any]:
    return {
        "command": command,
        "args": ["--transport", transport],
        "env": {},
    }


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError("Claude config file must contain a JSON object")
    return obj


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Claude desktop to load Skill Autopilot MCP")
    parser.add_argument("--config-path", default=str(DEFAULT_CLAUDE_CONFIG))
    parser.add_argument("--server-name", default="skill-autopilot")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--command", default=None, help="Override MCP command path")
    parser.add_argument("--print-only", action="store_true", help="Print the JSON snippet only")
    parser.add_argument("--apply", action="store_true", help="Write to Claude config file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    command = args.command or _resolve_mcp_command()
    server_entry = _build_server_entry(command=command, transport=args.transport)
    if args.print_only or not args.apply:
        print(json.dumps({"mcpServers": {args.server_name: server_entry}}, indent=2))
        return

    config_path = Path(args.config_path).expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    current = _load_json(config_path)

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if config_path.exists():
        backup = config_path.with_suffix(config_path.suffix + f".bak.skill-autopilot.{stamp}")
        backup.write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    mcp_servers = current.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        mcp_servers = {}
    mcp_servers[args.server_name] = server_entry
    current["mcpServers"] = mcp_servers

    config_path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Claude config: {config_path}")
    print("Restart Claude desktop to load the MCP server.")


if __name__ == "__main__":
    main()
