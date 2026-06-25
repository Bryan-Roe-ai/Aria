#!/usr/bin/env bash
# Kick off cloud orchestrate root planner for goal "AGI".
# Requires: CURSOR_API_KEY (user key), bun, orchestrate skill scripts.
set -euo pipefail

GOAL="${1:-AGI}"
REPO="${ORCHESTRATE_REPO:-https://github.com/Bryan-Roe/Aria.git}"
REF="${ORCHESTRATE_REF:-main}"
SCRIPTS="/home/vscode/.cursor/plugins/cache/cursor-public/orchestrate/e46364b8be46000b7df0f260550cd712afbb8d36/skills/orchestrate/scripts"

if [[ -z "${CURSOR_API_KEY:-}" ]]; then
  echo "BLOCKED: CURSOR_API_KEY is unset." >&2
  echo "Create a user API key at https://cursor.com/dashboard/integrations then:" >&2
  echo "  export CURSOR_API_KEY=\"cursor_...\"" >&2
  echo "  $0" >&2
  exit 2
fi

command -v bun >/dev/null 2>&1 || {
  echo "BLOCKED: bun not found. Install: curl -fsSL https://bun.sh/install | bash" >&2
  exit 3
}

[[ -d "$SCRIPTS" ]] || { echo "BLOCKED: orchestrate scripts not found at $SCRIPTS" >&2; exit 4; }

if [[ ! -d "$SCRIPTS/node_modules" ]]; then
  echo "Installing orchestrate CLI deps..."
  (cd "$SCRIPTS" && bun install)
fi

cd "$SCRIPTS"
exec bun cli.ts kickoff "$GOAL" --repo "$REPO" --ref "$REF"
