```prompt
---
agent: agent
description: "Implement soft delete pattern with data retention"
---
# Soft Delete Pattern
## Task
Implement soft delete instead of hard delete for data preservation.
## Requirements
1. Add is_deleted flag and deleted_at timestamp. 2. Filter deleted records from default queries.
3. Support restore (undelete) operation. 4. Hard delete after retention period.
5. Update indexes and constraints for soft delete.
## Constraints
- Default queries exclude deleted. Unique constraints must account for soft delete. Cleanup automated.
## Success Criteria
- Records soft-deleted and restorable. Queries correct. Hard delete after retention.
```
