```prompt
---
agent: agent
description: Detect expensive query patterns and remove data access bottlenecks.
---
Task:
Profile data queries to find slow, frequent, and high-cardinality access paths.
Requirements:
Report top queries by total time, call count, rows scanned, and index usage.
Constraints:
No unsafe schema changes in-place; preserve result correctness and authorization rules.
Success Criteria:
Deliver a ranked hotspot list, concrete query/index fixes, and measured gains.
```
