#!/usr/bin/env sh
set -eu

log() { printf '\n[post-create] %s\n' "$*"; }

retry() {
  # retry <attempts> <sleep_seconds> <command...>
  attempts="$1"; shift
  delay="$1"; shift
  n=1
  while true; do
    if "$@"; then
      return 0
    fi
    if [ "$n" -ge "$attempts" ]; then
      return 1
    fi
    log "Command failed (attempt $n/$attempts). Retrying in ${delay}s: $*"
    sleep "$delay"
    n=$((n + 1))
  done
}

log "Python / pip bootstrap"
retry 3 5 python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
  log "Installing requirements.txt"
  retry 3 5 python -m pip install -r requirements.txt
fi

if [ -f requirements-dev.txt ]; then
  log "Installing requirements-dev.txt"
  retry 3 5 python -m pip install -r requirements-dev.txt
fi

# Ensure user-level npm bin exists and is on PATH for this shell
mkdir -p /home/vscode/.npm-global/bin || true
export NPM_CONFIG_PREFIX="/home/vscode/.npm-global"
export PATH="/home/vscode/.npm-global/bin:$PATH"

if command -v npm >/dev/null 2>&1; then
  if ! command -v func >/dev/null 2>&1; then
    log "Installing Azure Functions Core Tools v4 (best effort)"
    # Best-effort: don't fail container creation if npm registry/network flakes
    if ! retry 3 8 npm install -g azure-functions-core-tools@4 --unsafe-perm true; then
      log "WARNING: Failed to install azure-functions-core-tools@4; container build will continue."
      log "You can retry manually later with: npm install -g azure-functions-core-tools@4 --unsafe-perm true"
    fi
  else
    log "func already installed; skipping"
  fi
fi

log "Post-create completed"