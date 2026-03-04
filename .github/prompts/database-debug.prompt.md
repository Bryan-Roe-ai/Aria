```prompt
---
agent: agent
description: "Debug and fix SQL or Cosmos DB connectivity, query performance, or schema issues"
---
# Database Debug

## Task
Diagnose and resolve a database issue in Aria's persistence layer.

## Context
- SQL engine: `shared/sql_engine.py`, `shared/sql_repository.py`
- Cosmos client: `shared/cosmos_client.py`
- Telemetry: `shared/telemetry.py`, `shared/tracing.py`
- Diagnostics: `/api/ai/status` reports SQL and Cosmos connectivity status

## Requirements
1. Check `/api/ai/status` JSON for SQL/Cosmos fields first.
2. Identify the failing query, connection, or configuration.
3. Fix the root cause in the appropriate `shared/` module.
4. Ensure queries are parameterized (no SQL injection risk).
5. Validate with unit tests.

## Constraints
- Never hardcode connection strings; use env vars.
- Cosmos: prefer point reads over cross-partition scans.
- Keep migration logic in `scripts/sql_migrate.py`.

## Success Criteria
- `/api/ai/status` shows healthy SQL/Cosmos status.
- Affected queries run successfully.
- No regression in existing tests.
```
