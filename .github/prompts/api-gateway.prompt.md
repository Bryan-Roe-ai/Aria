```prompt
---
agent: agent
description: "Implement API gateway pattern for microservice routing"
---
# API Gateway
## Task
Implement API gateway for microservice routing.
## Requirements
1. Route requests to appropriate backend services.
2. Aggregate responses from multiple services.
3. Handle service discovery and load balancing.
4. Implement circuit breaker for failing services.
5. Add cross-cutting concerns (auth, logging, rate limiting).
## Constraints
- Gateway must not become a bottleneck. Keep routing logic simple. Handle partial failures.
## Success Criteria
- Requests routed correctly. Failed services don't cascade. Gateway stays performant.
```
