```prompt
---
agent: agent
description: "Optimize SQL query performance with indexing and EXPLAIN"
---
# SQL Query Optimization
## Task
Optimize slow SQL queries for better performance.
## Requirements
1. Run EXPLAIN/EXPLAIN ANALYZE on slow queries. 2. Add appropriate indexes based on query patterns.
3. Eliminate N+1 query patterns. 4. Use query hints where needed.
5. Benchmark before and after optimization.
## Constraints
- Index only for proven slow queries. Consider write impact. Benchmark on production-like data.
## Success Criteria
- Query time reduced significantly. Index usage confirmed. No regressions.
```
