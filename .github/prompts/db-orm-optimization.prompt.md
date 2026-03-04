```prompt
---
agent: agent
description: "Implement ORM query optimization and N+1 prevention"
---
# ORM Query Optimization
## Task
Optimize ORM queries and eliminate N+1 patterns.
## Requirements
1. Use eager loading (joinedload/selectinload). 2. Detect N+1 with query logging.
3. Use bulk queries instead of per-item. 4. Profile ORM query count per request.
5. Use raw SQL for complex queries.
## Constraints
- Log query count per request. Alert on > 20 queries. Profile in development always.
## Success Criteria
- N+1 eliminated. Query count per request minimized. Complex queries use raw SQL.
```
