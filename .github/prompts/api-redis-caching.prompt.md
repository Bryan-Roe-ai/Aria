```prompt
---
agent: agent
description: "Implement API response caching with Redis"
---
# API Redis Caching
## Task
Implement API response caching with Redis.
## Requirements
1. Cache GET responses with configurable TTL. 2. Generate cache keys from URL + query params + user.
3. Invalidate cache on write operations. 4. Support cache warming for popular endpoints.
5. Monitor cache hit/miss ratio.
## Constraints
- Cache only GET requests. Don't cache user-specific data without user in key. Set TTL always.
## Success Criteria
- Cache hit rate > 80% for read-heavy endpoints. Invalidation works. Metrics tracked.
```
