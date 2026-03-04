```prompt
---
agent: agent
description: "Test rollback procedures for deployments and data changes"
---
# Rollback Tests
## Task
Write tests for rollback procedures.
## Requirements
1. Test deployment rollback restores previous version.
2. Test database rollback reverts schema changes.
3. Test configuration rollback restores previous settings.
4. Test partial rollback of multi-step operations.
5. Test rollback idempotency (safe to run multiple times).
## Constraints
- Rollbacks must be tested independently. Verify state after rollback matches pre-change.
## Success Criteria
- Rollbacks restore previous state exactly. State verified after rollback. Idempotent.
```
