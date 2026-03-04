```prompt
---
agent: agent
description: "Implement materialized view pattern for optimized reads"
---
# Materialized View
## Task
Implement materialized views for optimized read queries.
## Requirements
1. Pre-compute query results into materialized form. 2. Update materialized view on source data changes.
3. Handle eventual consistency. 4. Monitor freshness.
5. Support view refresh strategies (eager, lazy, scheduled).
## Constraints
- Accept staleness within configured window. Scheduled refresh for batch, eager for critical.
## Success Criteria
- Reads significantly faster. Staleness within window. Refresh strategy appropriate.
```
