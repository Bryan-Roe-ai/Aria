#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: scripts/start_local_coding_stack.sh [--status|--stop]

Default behavior:
  - Ensures Ollama API is running on 127.0.0.1:11434
  - Starts Azure Functions host in the foreground

Options:
  --status   Show Ollama and Functions status
  --stop     Stop local Functions host and Ollama serve processes
EOF
  exit 0
fi

if [[ "${1:-}" == "--status" ]]; then
  echo "[ollama]"
  if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "running"
  else
    echo "not running"
  fi

  echo
  echo "[func]"
  if pgrep -f "func host start" >/dev/null 2>&1; then
    echo "running"
  else
    echo "not running"
  fi
  exit 0
fi

if [[ "${1:-}" == "--stop" ]]; then
  pkill -f "func host start" >/dev/null 2>&1 || true
  pkill -f "ollama serve" >/dev/null 2>&1 || true
  echo "Stopped local Functions host and Ollama serve processes."
  exit 0
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama is not installed. Install it first: https://ollama.ai"
  exit 1
fi

if ! command -v func >/dev/null 2>&1; then
  echo "func is not installed. Install Azure Functions Core Tools first."
  exit 1
fi

started_ollama=0
if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama already running on 127.0.0.1:11434"
else
  echo "Starting Ollama server..."
  nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  started_ollama=1

  for _ in {1..20}; do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done

  if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Failed to start Ollama. Check /tmp/ollama-serve.log"
    exit 1
  fi
fi

if [[ ${started_ollama} -eq 1 ]]; then
  echo "Ollama started."
fi

echo "Starting Azure Functions host from ${ROOT_DIR}"
cd "${ROOT_DIR}"
exec func host start
