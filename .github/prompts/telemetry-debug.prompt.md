```prompt
---
agent: agent
description: "Debug telemetry, tracing, or Cosmos DB observability pipeline issues"
---
# Telemetry Debug

## Task
Diagnose and fix issues in Aria's telemetry, tracing, or Cosmos DB observability pipeline.

## Context
- Telemetry: `shared/telemetry.py`
- Tracing: `shared/tracing.py`
- Cosmos client: `shared/cosmos_client.py`
- DB logging: `shared/db_logging.py`
- Diagnostics: `/api/ai/status` reports telemetry and Cosmos status

## Requirements
1. Check `/api/ai/status` for telemetry/Cosmos connectivity indicators.
2. Identify missing spans, dropped events, or failed writes.
3. Fix the issue in the appropriate `shared/` module.
4. Ensure spans are lightweight and do not log PII.
5. Validate with existing tests (`tests/test_otel_callback.py`, `tests/test_shared_tracing.py`).

## Constraints
- Never log PII in telemetry spans.
- Cosmos operations: prefer point reads; set reasonable RU budgets.
- Keep tracing overhead minimal; avoid deep nesting of spans.
- Use env vars for endpoints and keys.

## Success Criteria
- Telemetry data flows end-to-end without drops.
- `/api/ai/status` shows healthy status.
- Related tests pass.
```
