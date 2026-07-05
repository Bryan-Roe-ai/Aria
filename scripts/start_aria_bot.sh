#!/usr/bin/env bash
# Lightweight launcher for the deterministic aria-bot loop.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="python3"
fi

exec "$PYTHON_BIN" -m aria_bot --repo-root "$REPO_ROOT" "$@"
