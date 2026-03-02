#!/usr/bin/env bash
# One-command local health automation for Aria repository.
# Runs fast validation, then optional test suites.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

choose_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    echo "$PYTHON_BIN"
    return
  fi

  local candidates=(
    "$REPO_ROOT/.venv/bin/python"
    "$REPO_ROOT/venv/bin/python"
    "$REPO_ROOT/.venv/Scripts/python.exe"
    "$REPO_ROOT/venv/Scripts/python.exe"
    "python3"
    "python"
  )

  for candidate in "${candidates[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1 || [[ -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done

  echo ""
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [--unit|--all|--validate-only]

Options:
  --unit           Run fast validate + unit tests (default)
  --all            Run fast validate + full test suite
  --validate-only  Run only fast validation
  -h, --help       Show this help message
EOF
}

MODE="unit"
case "${1:-}" in
  ""|--unit) MODE="unit" ;;
  --all) MODE="all" ;;
  --validate-only) MODE="validate-only" ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: $1"
    usage
    exit 2
    ;;
esac

PYTHON_CMD="$(choose_python)"
if [[ -z "$PYTHON_CMD" ]]; then
  echo "❌ No Python executable found. Set PYTHON_BIN or create .venv/venv."
  exit 1
fi

echo "🔧 Using Python: $PYTHON_CMD"

echo "\n[1/2] Fast repository validation"
"$PYTHON_CMD" "$REPO_ROOT/scripts/fast_validate.py"

if [[ "$MODE" == "validate-only" ]]; then
  echo "\n✅ Completed validate-only run"
  exit 0
fi

echo "\n[2/2] Test run ($MODE)"
if [[ "$MODE" == "all" ]]; then
  "$PYTHON_CMD" "$REPO_ROOT/scripts/test_runner.py" --all
else
  "$PYTHON_CMD" "$REPO_ROOT/scripts/test_runner.py" --unit
fi

echo "\n✅ Repository health automation completed"
