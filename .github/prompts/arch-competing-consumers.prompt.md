```prompt
---
agent: agent
description: "Implement competing consumers pattern for load distribution"
---
# Competing Consumers
## Task
Implement competing consumers for message processing.
## Requirements
1. Multiple consumers process from shared queue. 2. Each message processed by exactly one consumer.
3. Handle consumer failures with redelivery. 4. Scale consumers based on queue depth.
5. Maintain message ordering within partition.
## Constraints
- At-least-once delivery. Consumers must be idempotent. Scale on queue depth.
## Success Criteria
- Messages processed reliably. Load distributed. Failures recovered. Ordering maintained.
```
