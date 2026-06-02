#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/data_out"
AZURITE_DIR="${ROOT_DIR}/.azurite"
STATUS_FILE="/tmp/aria-agi-status.json"
AZURITE_LOG="${LOG_DIR}/azurite.log"
FUNC_LOG="${LOG_DIR}/func-host.log"

print_usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Options:
  --cycles N             Number of launcher cycles to run (default: 1, 0 = infinite)
  --short-break-sec N    Seconds to sleep between normal cycles (default: 30)
  --long-break-sec N     Seconds to sleep after every long-break interval (default: 300)
  --long-break-every N   Use the long break after every N cycles (default: 5)
  --help, -h            Show this help message

Environment overrides:
  AGI_LAUNCH_CYCLES
  AGI_SHORT_BREAK_SEC
  AGI_LONG_BREAK_SEC
  AGI_LONG_BREAK_EVERY

Docs: docs/guides/AGI_LAUNCHER_SERVICE.md (VS Code tasks + systemd user service)
EOF
}

CYCLES="${AGI_LAUNCH_CYCLES:-1}"
SHORT_BREAK_SEC="${AGI_SHORT_BREAK_SEC:-30}"
LONG_BREAK_SEC="${AGI_LONG_BREAK_SEC:-300}"
LONG_BREAK_EVERY="${AGI_LONG_BREAK_EVERY:-5}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cycles)
      CYCLES="${2:-1}"
      shift 2
      ;;
    --short-break-sec)
      SHORT_BREAK_SEC="${2:-30}"
      shift 2
      ;;
    --long-break-sec)
      LONG_BREAK_SEC="${2:-300}"
      shift 2
      ;;
    --long-break-every)
      LONG_BREAK_EVERY="${2:-5}"
      shift 2
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$CYCLES" =~ ^[0-9]+$ ]] || ! [[ "$SHORT_BREAK_SEC" =~ ^[0-9]+$ ]] || ! [[ "$LONG_BREAK_SEC" =~ ^[0-9]+$ ]] || ! [[ "$LONG_BREAK_EVERY" =~ ^[0-9]+$ ]]; then
  echo "[startup: agi] cycle and break values must be non-negative integers." >&2
  exit 2
fi

mkdir -p "${LOG_DIR}" "${AZURITE_DIR}"

ensure_services() {
  if ! lsof -iTCP:10000 -sTCP:LISTEN >/dev/null 2>&1; then
    nohup npx --yes azurite --silent --location "${AZURITE_DIR}" --blobPort 10000 --queuePort 10001 --tablePort 10002 >"${AZURITE_LOG}" 2>&1 &
  fi

  if ! lsof -iTCP:7071 -sTCP:LISTEN >/dev/null 2>&1; then
    if command -v func >/dev/null 2>&1; then
      nohup func host start >"${FUNC_LOG}" 2>&1 &
    else
      echo "[startup: agi] Azure Functions Core Tools (func) not found on PATH; cannot start local host."
    fi
  fi
}

wait_for_status() {
  local attempt
  for attempt in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:7071/api/agi/status >"${STATUS_FILE}" 2>/dev/null; then
      cat "${STATUS_FILE}" | python3 -m json.tool
      return 0
    fi
    sleep 1
  done

  return 1
}

sleep_for_break() {
  local cycle_num="$1"
  local break_label="short"
  local break_sec="$SHORT_BREAK_SEC"

  if [[ "$LONG_BREAK_EVERY" -gt 0 ]] && (( cycle_num % LONG_BREAK_EVERY == 0 )); then
    break_label="long"
    break_sec="$LONG_BREAK_SEC"
  fi

  if [[ "$break_sec" -gt 0 ]]; then
    echo "[startup: agi] Cycle ${cycle_num} complete; sleeping ${break_label} break for ${break_sec}s..."
    sleep "$break_sec"
  fi
}

cycle_num=1
infinite=0
if [[ "$CYCLES" -eq 0 ]]; then
  infinite=1
fi

while :; do
  echo "[startup: agi] Cycle ${cycle_num} starting..."
  ensure_services

  if ! wait_for_status; then
    echo "[startup: agi] AGI status endpoint did not come up in time."
    tail -20 "${AZURITE_LOG}" 2>/dev/null || true
    tail -20 "${FUNC_LOG}" 2>/dev/null || true
    exit 1
  fi

  if [[ "$infinite" -eq 0 && "$cycle_num" -ge "$CYCLES" ]]; then
    exit 0
  fi

  cycle_num=$((cycle_num + 1))
  sleep_for_break "$((cycle_num - 1))"
done
