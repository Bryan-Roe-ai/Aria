```prompt
---
agent: agent
description: "Implement API caching with ETags and Cache-Control"
---
# API Caching
## Task
Implement HTTP caching for API responses.
## Requirements
1. Set `Cache-Control` headers (max-age, no-cache, private).
2. Implement ETag generation and `If-None-Match` validation.
3. Return 304 Not Modified for unchanged resources.
4. Support `Last-Modified` and `If-Modified-Since`.
5. Implement cache invalidation on writes.
## Constraints
- Never cache authenticated user-specific data publicly. Invalidate on mutations.
## Success Criteria
- Caching headers set correctly. 304 responses work. Cache invalidated on writes.
```
