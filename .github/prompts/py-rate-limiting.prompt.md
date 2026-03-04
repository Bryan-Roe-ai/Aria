```prompt
---
agent: agent
description: "Implement rate limiting for API endpoints and resource protection"
---
# Rate Limiting
## Task
Implement rate limiting for API endpoints and resource protection.
## Requirements
1. Choose algorithm (token bucket, sliding window, fixed window).
2. Support per-user and global rate limits.
3. Return standard HTTP 429 with Retry-After header.
4. Implement rate limit storage (in-memory, Redis).
5. Allow configurable limits per endpoint.
## Constraints
- Rate limit storage must be thread-safe.
- Don't rate-limit health check endpoints.
- Set sensible defaults that don't break legitimate usage.
## Success Criteria
- API endpoints are protected from abuse.
- Rate limit headers are returned in all responses.
- Legitimate users are not impacted.
```
