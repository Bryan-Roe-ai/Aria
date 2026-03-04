```prompt
---
agent: agent
description: "Implement API retry-after logic for service overload"
---
# API Retry-After
## Task
Implement Retry-After response handling for overload protection.
## Requirements
1. Return `Retry-After` header with seconds or HTTP-date. 2. Use with 429 (rate limit), 503 (overload), 301 (moved).
3. Calculate retry time based on queue depth / load. 4. Add jitter to prevent thundering herd.
5. Client SDK should respect Retry-After automatically.
## Constraints
- Retry-After must be honest (don't set too short). Include jitter. Document in API spec.
## Success Criteria
- Retry-After set on overload responses. Clients wait appropriately. Jitter prevents spikes.
```
