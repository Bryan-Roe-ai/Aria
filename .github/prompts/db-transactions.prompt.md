```prompt
---
agent: agent
description: "Implement database transaction management and isolation levels"
---
# Transaction Management
## Task
Implement proper transaction management with appropriate isolation.
## Requirements
1. Choose isolation level (READ COMMITTED, SERIALIZABLE). 2. Handle deadlock detection and retry.
3. Keep transactions short. 4. Use savepoints for partial rollback.
5. Monitor transaction duration.
## Constraints
- Prefer READ COMMITTED. Use SERIALIZABLE only when required. Retry on deadlock (max 3).
## Success Criteria
- Transactions consistent. Deadlocks handled. Duration monitored. Isolation appropriate.
```
