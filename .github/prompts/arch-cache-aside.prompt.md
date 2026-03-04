```prompt
---
agent: agent
description: "Implement cache-aside pattern for data access"
---
# Cache-Aside Pattern
## Task
Implement cache-aside (lazy-loading) caching pattern.
## Requirements
1. Check cache before database query. 2. Load from DB on cache miss and populate cache.
3. Invalidate cache on writes. 4. Set TTL to prevent stale data.
5. Handle cache failures gracefully (fall through to DB).
## Constraints
- Cache miss is not an error. TTL prevents staleness. Falls back to DB on cache failure.
## Success Criteria
- Cache hit ratio > 80%. Stale data prevented. DB fallback works. Performance improved.
```
