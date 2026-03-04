```prompt
---
agent: agent
description: "Implement database deadlock detection and resolution"
---
# Deadlock Resolution
## Task
Detect and resolve database deadlocks.
## Requirements
1. Enable deadlock monitoring. 2. Log deadlock details (blocked/blocking).
3. Implement automatic retry on deadlock. 4. Analyze deadlock patterns.
5. Redesign queries to prevent common deadlocks.
## Constraints
- Retry up to 3 times on deadlock. Log deadlock graph. Address root cause, not just retry.
## Success Criteria
- Deadlocks detected and logged. Retries recover. Root causes addressed.
```
