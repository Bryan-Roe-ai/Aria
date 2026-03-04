```chatagent
---
name: database-and-telemetry
description: SQL/Cosmos/telemetry diagnostics, migrations, and query optimization for Aria's persistence layer.
---

# Database & Telemetry Agent

## When to Use

- SQL schema migrations or `sql_engine.py` / `sql_repository.py` changes.
- Cosmos DB container config, partition key, or throughput tuning.
- Telemetry pipeline (`shared/telemetry.py`, `shared/tracing.py`) instrumentation or debugging.
- Query performance issues, threshold tuning, or metric cleanup scripts.
- `/api/ai/status` persistence diagnostics.

## Workflow

1. **Diagnose** — Check `/api/ai/status` for SQL/Cosmos connectivity first.
2. **Inspect** — Read `shared/sql_engine.py`, `shared/cosmos_client.py`, `shared/telemetry.py` and related test files.
3. **Plan migration** — For schema changes, write a migration script under `scripts/sql_migrate.py` or a new migration file; never ALTER in production without a rollback path.
4. **Implement** — Keep DB logic in `shared/`; avoid scattering raw queries across route handlers.
5. **Validate** — Run `python scripts/test_runner.py --unit` and check `/api/ai/status` SQL/Cosmos fields.

## Guardrails

- Never hardcode connection strings; use env vars (`SQL_CONNECTION_STRING`, `COSMOS_ENDPOINT`, `COSMOS_KEY`).
- Cosmos operations: prefer point reads over cross-partition queries; set reasonable RU budgets.
- SQL: parameterize all queries to prevent injection.
- Telemetry: keep spans lightweight; avoid logging PII.
- Test DB changes with the test suite before deploying.
```
