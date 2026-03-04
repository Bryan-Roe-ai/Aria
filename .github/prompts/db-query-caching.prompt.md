```prompt
---
agent: agent
description: "Implement database query caching strategies"
---
# Query Caching
## Task
Implement query caching for frequently accessed data.
## Requirements
1. Identify cache-worthy queries (frequent, stable, expensive). 2. Implement cache invalidation on writes.
3. Set TTL per query type. 4. Use Redis or application-level cache.
5. Monitor cache hit rate.
## Constraints
- Cache only idempotent queries. Invalidate on relevant writes. TTL prevents staleness.
## Success Criteria
- Cache hit rate > 80%. Invalidation correct. Performance improved. Staleness prevented.
```
