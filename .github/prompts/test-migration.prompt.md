```prompt
---
agent: agent
description: "Test database migration scripts forward and backward"
---
# Migration Tests
## Task
Write tests for database migration scripts.
## Requirements
1. Test forward migration applies schema changes.
2. Test backward migration reverts schema changes.
3. Test data migration preserves existing data.
4. Test migration ordering and dependencies.
5. Test idempotency of migration scripts.
## Constraints
- Use test database. Test both up and down migrations. Verify schema after each step.
## Success Criteria
- Migrations apply and revert cleanly. Data preserved. Ordering correct.
```
