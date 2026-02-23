# macOS Install Guide

## Requirements
1. macOS with terminal access.
2. Python 3.11+ (`python3 --version`).
3. Git.

## One-command install
```bash
git clone https://github.com/tudorpetraru/Skills.git
cd Skills
./scripts/install_macos.sh
```

This creates a dedicated runtime at `~/.skill-autopilot/venv`, installs the app, and runs health checks.

## Optional: configure Claude MCP automatically
```bash
./scripts/install_macos.sh --apply-claude-config
```

Manual alternative:
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-configure-claude --apply
```

## Launch
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-ui
```

## Verify installation
```bash
~/.skill-autopilot/venv/bin/skill-autopilot-doctor
```

Expected critical checks:
1. Python version is >= 3.11.
2. Config can be created/read.
3. State directory is writable.
4. At least one catalog source exists.
5. `skill-autopilot-mcp` is callable.

## Optional: enable LLM industry detection
For smarter project classification from unstructured briefs:
```bash
~/.skill-autopilot/venv/bin/pip install -e '/path/to/Skills[llm]'
```
Then set your API key in your shell profile or Claude MCP config env:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Upgrade
From an existing clone:
```bash
cd Skills
./scripts/install_macos.sh
```

This reinstalls the latest local code into the dedicated venv.

## Uninstall
```bash
rm -rf ~/.skill-autopilot
rm -rf ~/.project-skill-router
```

If you added Claude MCP config, remove `mcpServers.skill-autopilot` from:
`~/Library/Application Support/Claude/claude_desktop_config.json`.
