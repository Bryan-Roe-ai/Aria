```prompt
---
agent: agent
description: "Implement leader election for distributed coordination"
---
# Leader Election
## Task
Implement leader election for distributed coordination.
## Requirements
1. Elect one leader among instances. 2. Leader handles coordination tasks.
3. Detect leader failure and re-elect. 4. Prevent split-brain scenarios.
5. Support graceful leadership transfer.
## Constraints
- Only one leader at any time. Heartbeat for failure detection. Fencing tokens prevent split-brain.
## Success Criteria
- Single leader elected. Failure detected and re-elected. No split-brain.
```
