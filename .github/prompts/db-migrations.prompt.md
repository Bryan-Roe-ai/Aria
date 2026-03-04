```prompt
---
agent: agent
description: "Write database migration scripts with forward and backward support"
---
# Database Migrations
## Task
Write database migration scripts supporting forward and backward migration.
## Requirements
1. Create numbered migration files. 2. Support up (apply) and down (revert).
3. Use transactions for atomicity. 4. Handle data migrations safely.
5. Test migrations on staging first.
## Constraints
- Backward-compatible migrations. Test up and down. Never modify existing migrations.
## Success Criteria
- Migrations apply and revert cleanly. Data preserved. Backward-compatible.
```
