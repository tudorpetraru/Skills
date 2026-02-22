#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PATH="${SKILL_AUTOPILOT_VENV:-$HOME/.skill-autopilot/venv}"
APPLY_CLAUDE_CONFIG="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --venv)
      VENV_PATH="$2"
      shift 2
      ;;
    --apply-claude-config)
      APPLY_CLAUDE_CONFIG="1"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

resolve_python() {
  local candidate
  for candidate in "$PYTHON_BIN" python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
      then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

if ! PYTHON_BIN="$(resolve_python)"; then
  echo "Python 3.11+ not found. Install Python 3.11+ and rerun." >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys
print(f"Using Python {sys.version.split()[0]}")
PY

mkdir -p "$(dirname "$VENV_PATH")"
"$PYTHON_BIN" -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install "$REPO_ROOT"

echo
echo "Running installation doctor checks..."
skill-autopilot-doctor

if [[ "$APPLY_CLAUDE_CONFIG" == "1" ]]; then
  echo
  echo "Updating Claude MCP config..."
  skill-autopilot-configure-claude --apply
fi

echo
echo "Install complete."
echo "Venv: $VENV_PATH"
echo "Run UI: $VENV_PATH/bin/skill-autopilot-ui"
echo "Run doctor: $VENV_PATH/bin/skill-autopilot-doctor"
echo "Configure Claude (preview): $VENV_PATH/bin/skill-autopilot-configure-claude --print-only"
echo "Configure Claude (apply):   $VENV_PATH/bin/skill-autopilot-configure-claude --apply"
