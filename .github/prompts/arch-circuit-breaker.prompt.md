```prompt
---
agent: agent
description: "Implement circuit breaker pattern with half-open state"
---
# Circuit Breaker
## Task
Implement circuit breaker for resilient external calls.
## Requirements
1. Track failure rate per dependency. 2. Open circuit after threshold failures.
3. Return fallback in open state. 4. Half-open state probes recovery.
5. Close circuit on successful probe.
## Constraints
- Per-dependency state. Configurable thresholds. Meaningful fallbacks. Log state transitions.
## Success Criteria
- Failures don't cascade. Circuit opens on threshold. Recovery detected automatically.
```
