```prompt
---
agent: agent
description: "Implement database audit trail for change tracking"
---
# Database Audit Trail
## Task
Implement audit trail to track all data changes.
## Requirements
1. Log INSERT, UPDATE, DELETE operations. 2. Record old and new values.
3. Include user, timestamp, and operation type. 4. Make audit records immutable.
5. Support audit queries by entity and time range.
## Constraints
- Audit tables separate from main tables. Immutable records. Minimal performance impact.
## Success Criteria
- All changes tracked. Old/new values captured. Audit queryable. Performance acceptable.
```
