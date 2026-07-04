#!/usr/bin/env bash
# Cross-platform fail-open runner for Python hook scripts.
#
# Cursor/VS Code agent hooks on Windows often execute in PowerShell 5.1, which
# does not support bash-style `cmd1 || cmd2`. Use this wrapper in hook JSON
# manifests instead of inline `||` chains.
#
# Usage: bash .github/hooks/scripts/run_python_hook.sh <hook_script.py>
#
# Exit 0 when Python is missing so hooks never block the agent on setup issues.

set -u

SCRIPT_PATH="${1:?usage: run_python_hook.sh <hook_script.py>}"

_run() {
  "$@" "$SCRIPT_PATH"
}

if command -v python3 >/dev/null 2>&1; then
  _run python3 && exit 0
fi

if command -v python >/dev/null 2>&1; then
  if python --version >/dev/null 2>&1; then
    _run python && exit 0
  fi
fi

if command -v py >/dev/null 2>&1; then
  _run py -3 && exit 0
fi

exit 0
