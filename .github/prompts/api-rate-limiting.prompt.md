```prompt
---
agent: agent
description: "Implement API rate limiting and throttling"
---
# API Rate Limiting
## Task
Implement rate limiting for API endpoint protection.
## Requirements
1. Set rate limits per user/API key/IP.
2. Return 429 Too Many Requests with `Retry-After` header.
3. Implement sliding window or token bucket algorithm.
4. Support different limits per endpoint tier.
5. Return rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).
## Constraints
- Rate limiting must not block health checks. Use distributed rate limiting for multi-instance.
## Success Criteria
- Rate limits enforced. Retry-After header set. Limit headers returned.
```
