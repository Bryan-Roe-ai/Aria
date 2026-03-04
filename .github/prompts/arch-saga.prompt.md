```prompt
---
agent: agent
description: "Implement saga pattern for distributed transactions"
---
# Saga Pattern
## Task
Implement saga pattern for distributed transaction coordination.
## Requirements
1. Define saga steps with compensating actions. 2. Implement choreography or orchestration.
3. Handle step failures with compensations. 4. Track saga state.
5. Implement timeouts for hung sagas.
## Constraints
- Every step needs a compensating action. Track state persistently. Timeout after 5 minutes.
## Success Criteria
- Saga coordinates multi-service transactions. Compensations run on failure. State tracked.
```
