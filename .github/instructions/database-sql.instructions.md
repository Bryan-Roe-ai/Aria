```instructions
---
name: "Database-SQL"
description: "Guidance for database/ schema definitions, migrations, and stored procedures"
applyTo: "database/**"
---
# Database – SQL

- `database/` contains SQL schema definitions (table DDL, stored procedures, views).
- Use `IF NOT EXISTS` / `IF EXISTS` guards for idempotent schema scripts.
- Table naming: `[dbo].[PascalCaseTableName]`.
- Column naming: `PascalCase` to match existing conventions.
- Always include primary keys and appropriate indexes.
- Parameterize all queries; never use string interpolation for user-supplied values.
- Embedding tables (`ChatMessageEmbeddings`): store float32 as little-endian binary.
- Keep migration scripts in `scripts/sql_migrate.py`; schema definitions in `database/`.
- Connection strings via env var `QAI_DB_CONN`; never hardcode.
- Document schema changes with inline comments and update related `shared/` modules.
```
