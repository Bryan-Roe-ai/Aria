```prompt
---
agent: agent
description: "Implement publisher-subscriber pattern for event distribution"
---
# Pub/Sub Pattern
## Task
Implement publisher-subscriber pattern for event distribution.
## Requirements
1. Define topics for event categories. 2. Publishers send events without knowing subscribers.
3. Subscribers filter by topics of interest. 4. Support durable subscriptions.
5. Handle subscriber failures.
## Constraints
- Loose coupling between publisher and subscriber. Durable for critical events. DLQ for failures.
## Success Criteria
- Events distributed to subscribers. Publishers decoupled. Durable subscriptions persist.
```
