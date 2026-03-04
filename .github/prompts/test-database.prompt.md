```prompt
---
agent: agent
description: "Test database operations with transactional rollback"
---
# Database Tests
## Task
Write database tests with transactional rollback for isolation.
## Requirements
1. Wrap each test in a transaction that rolls back after.
2. Use test-specific database or schema.
3. Test CRUD operations with real SQL.
4. Verify constraints, indexes, and triggers.
5. Test migration scripts forward and backward.
## Constraints
- Never run database tests against production. Use rollback, not DELETE for cleanup.
## Success Criteria
- Database operations verified with real SQL. Tests isolated via transactions. Migrations tested.
```
