#!/usr/bin/env bash
# Verify local AGI stack on :7071 (local_dev_adapter or func host).
set -euo pipefail

PORT="${FUNC_PORT:-7071}"
BASE="http://127.0.0.1:${PORT}"

fail() { echo "FAIL: $*" >&2; exit 1; }

code=$(curl -s -o /tmp/agi_status.json -w '%{http_code}' "${BASE}/api/agi/status" || echo "000")
[[ "$code" == "200" ]] || fail "GET /api/agi/status HTTP ${code} (is make start-local-status or make start-functions running?)"

python3 - <<'PY'
import json, sys
d = json.load(open("/tmp/agi_status.json"))
assert d.get("status") == "ok", d
assert d.get("available") is True, d
backends = d.get("backends") or {}
print("OK status=ok available=true persistence=", backends.get("persistence", {}).get("type"))
PY

analyze_code=$(curl -s -o /tmp/agi_analyze.json -w '%{http_code}' \
  -X POST "${BASE}/api/agi/analyze" \
  -H 'Content-Type: application/json' \
  -d '{"query":"health check"}' || echo "000")
[[ "$analyze_code" == "200" ]] || fail "POST /api/agi/analyze HTTP ${analyze_code}"

python3 - <<'PY'
import json
d = json.load(open("/tmp/agi_analyze.json"))
assert d.get("status") == "ok", d
print("OK analyze status=ok agent=", (d.get("routing") or {}).get("selected_agent"))
PY

echo "verify_agi_local: all checks passed on ${BASE}"
