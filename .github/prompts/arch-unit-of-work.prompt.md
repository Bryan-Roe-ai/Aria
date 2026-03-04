```prompt
---
agent: agent
description: "Implement unit of work pattern for transaction management"
---
# Unit of Work
## Task
Implement unit of work for transaction management.
## Requirements
1. Track changes to entities within transaction. 2. Commit all changes atomically.
3. Rollback on any failure. 4. Coordinate multiple repositories.
5. Prevent partial writes.
## Constraints
- One transaction per unit of work. All-or-nothing commits. Clean up on failure.
## Success Criteria
- Changes committed atomically. Failures roll back everything. No partial writes.
```
