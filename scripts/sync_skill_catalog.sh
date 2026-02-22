#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/library/skills/"
DST="$REPO_ROOT/skill_autopilot/skills/"

mkdir -p "$DST"
rsync -a --delete "$SRC" "$DST"
echo "Synced skill catalog:"
echo "  from: $SRC"
echo "  to:   $DST"
