```prompt
---
agent: agent
description: "Implement priority queue pattern for task scheduling"
---
# Priority Queue
## Task
Implement priority queue pattern for task scheduling.
## Requirements
1. Define priority levels (critical, high, normal, low). 2. Process higher-priority tasks first.
3. Prevent starvation of low-priority tasks. 4. Support priority escalation.
5. Monitor queue depth per priority.
## Constraints
- No starvation: promote after max wait time. Separate queues per priority. Monitor depths.
## Success Criteria
- Higher priority processed first. No starvation. Escalation works. Depths monitored.
```
