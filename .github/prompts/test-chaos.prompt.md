```prompt
---
agent: agent
description: "Implement chaos tests for resilience and fault tolerance"
---
# Chaos Tests
## Task
Implement chaos tests to verify system resilience.
## Requirements
1. Inject random failures in network, disk, and memory.
2. Test graceful degradation under partial failures.
3. Test circuit breaker activation and recovery.
4. Test data consistency after chaos events.
5. Measure recovery time and data loss.
## Constraints
- Run only in test environments. Set blast radius limits. Document failure modes.
## Success Criteria
- System degrades gracefully. Recovers after chaos stops. No data corruption.
```
