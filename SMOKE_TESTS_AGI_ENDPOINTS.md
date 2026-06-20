# AGI Smoke Tests — Quick Reference

Quick verification that AGI endpoints and LM Studio integration are working.

## Prerequisites

Ensure Azure Functions is running on port 7071:

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
func host start --port 7071
```

## Smoke Tests (curl)

### 1. AGI Status Endpoint

Check that `/api/agi/status` exposes LM Studio agent tools:

```bash
# Get full status (includes agent_tools field)
curl -s http://127.0.0.1:7071/api/agi/status | jq '.agent_tools.["lmstudio-specialist"]'

# Expected output: list of tool names
# ["chat_completion", "list_models", "server_status"]
```

### 2. AGI Analyze Endpoint

Send a reasoning request:

```bash
curl -s -X POST http://127.0.0.1:7071/api/agi/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"reason through this architecture"}' | jq '.reasoning'
```

### 3. AGI Stream Endpoint

Verify SSE streaming works:

```bash
curl -N -s -X POST http://127.0.0.1:7071/api/agi/stream \
  -H "Content-Type: application/json" \
  -d '{"query":"stream a short response"}' | head -20
```

## Automated Smoke Tests

Run the pytest smoke suite:

```bash
# Run all AGI smoke tests
.venv/bin/python -m pytest tests/test_agi_smoke.py -v

# Run just the tool metadata tests
.venv/bin/python -m pytest tests/test_agi_smoke.py::test_agi_status_exposes_lmstudio_agent_tools -v
.venv/bin/python -m pytest tests/test_agi_smoke.py::test_agi_status_response_schema -v
.venv/bin/python -m pytest tests/test_agi_smoke.py::test_agi_status_agent_tools_deterministic -v

# Run full endpoint regression (52 tests)
.venv/bin/python -m pytest tests/test_function_app_endpoints.py -q
```

## Contract Validation

The `/api/agi/status` endpoint response includes:

```json
{
  "status": "ok|degraded|error",
  "available": true|false,
  "provider": {"name": "..."},
  "reasoning": {"total_reasoning_chains": ...},
  "agent_tools": {
    "lmstudio-specialist": ["chat_completion", "list_models", "server_status"],
    "...": [...]
  },
  "endpoints": ["/api/agi/status", "/api/agi/analyze", "/api/agi/stream", ...]
}
```

### Guard Test Guarantees

- **test_agi_status_response_schema**: Validates response structure (required fields, types, sorting)
- **test_agi_status_agent_tools_deterministic**: Ensures output is stable across calls (no duplicates, consistent ordering)

## Troubleshooting

| Issue                                | Solution                                                        |
| ------------------------------------ | --------------------------------------------------------------- |
| `curl: (7) Failed to connect`        | Ensure `func host start` is running on port 7071                |
| `agent_tools` field missing          | Check `agi_provider._AGENT_REGISTRY` is accessible              |
| Tool names not sorted                | Verify `sorted(set(...))` logic in `function_app.py` agi_status |
| Non-string tools in list             | Check `agi_provider.py` tool configuration structure            |
