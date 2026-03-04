```prompt
---
agent: agent
description: "Implement the circuit breaker pattern for fault tolerance"
---
# Circuit Breaker
## Task
Implement circuit breaker for fault-tolerant external service calls.
## Requirements
1. Track failure rates for external service calls.
2. Open circuit after failure threshold is exceeded.
3. Enter half-open state after cooldown period.
4. Close circuit when health check passes.
5. Provide fallback responses when circuit is open.
## Constraints
- Separate circuit state per external service.
- Make thresholds configurable (failure count, time window, cooldown).
- Log all state transitions.
## Success Criteria
- Failing services don't cause cascading failures.
- Circuit opens quickly on persistent failures.
- Service recovery is detected and circuit closes.
```
