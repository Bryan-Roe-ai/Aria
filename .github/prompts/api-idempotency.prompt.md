```prompt
---
agent: agent
description: "Implement idempotency keys for safe API retries"
---
# API Idempotency
## Task
Implement idempotency keys for safe API retries.
## Requirements
1. Accept `Idempotency-Key` header on POST/PATCH requests.
2. Store results by key for replay.
3. Return cached result for duplicate keys.
4. Set key expiry (24 hours).
5. Handle concurrent requests with same key.
## Constraints
- Only for non-GET requests. Use distributed storage for multi-instance. Expire keys.
## Success Criteria
- Duplicate requests return same result. Concurrent requests handled. Keys expire.
```
