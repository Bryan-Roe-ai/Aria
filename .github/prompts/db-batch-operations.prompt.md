```prompt
---
agent: agent
description: "Implement database batch operations for bulk data processing"
---
# Database Batch Operations
## Task
Implement efficient batch operations for bulk data processing.
## Requirements
1. Use bulk INSERT with batch sizes. 2. Implement batch UPDATE with WHERE IN.
3. Handle batch failures with partial success. 4. Use transactions for consistency.
5. Monitor batch throughput.
## Constraints
- Batch size 1000 rows default. Transaction per batch. Log failed records.
## Success Criteria
- Bulk operations fast. Batch failures handled. Throughput monitored.
```
