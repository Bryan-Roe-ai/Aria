```prompt
---
agent: agent
description: "Implement API circuit breaker for external service calls"
---
# API Circuit Breaker
## Task
Implement circuit breaker pattern for external API calls.
## Requirements
1. Track failure rate per external service.
2. Open circuit after threshold (5 failures in 60s).
3. Return fallback response when circuit is open.
4. Half-open state for probing recovery.
5. Log circuit state changes.
## Constraints
- Per-service circuit state. Configurable thresholds. Fallback must be meaningful.
## Success Criteria
- Circuit opens on failures. Fallback returned. Recovers when service is back.
```
