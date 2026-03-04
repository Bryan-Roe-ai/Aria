```prompt
---
agent: agent
description: "Write a database migration script for SQL schema changes"
---
# Migration Script

## Task
Create a safe, reversible SQL migration script for a schema change.

## Context
- SQL engine: `shared/sql_engine.py`
- Migration runner: `scripts/sql_migrate.py`
- Existing schemas: `database/` directory
- Connection: env var `QAI_DB_CONN`

## Requirements
1. Define the schema change (ADD/ALTER/DROP column, new table, index).
2. Write an idempotent migration script that checks preconditions.
3. Include a rollback section (reverse migration).
4. Parameterize all queries; no string interpolation with user data.
5. Test migration against a local/dev database first.

## Constraints
- Never run migrations in production without a tested rollback.
- Use `IF NOT EXISTS` / `IF EXISTS` guards for idempotency.
- Connection strings via env vars only.
- Document the migration purpose and expected impact.

## Success Criteria
- Migration runs cleanly on a fresh database.
- Migration is idempotent (safe to re-run).
- Rollback restores previous schema state.
- Existing queries/code updated to match new schema.
```
