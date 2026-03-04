```prompt
---
agent: agent
description: "Implement event-driven architecture with message broker"
---
# Event-Driven Architecture
## Task
Design event-driven architecture with message broker.
## Requirements
1. Define events with schema versioning. 2. Implement publish/subscribe messaging.
3. Guarantee at-least-once delivery. 4. Handle message ordering and deduplication.
5. Implement dead-letter queues for failures.
## Constraints
- Events are immutable facts. Schema evolution with backward compatibility. DLQ for poison messages.
## Success Criteria
- Events flow reliably. Ordering maintained. Duplicates handled. Dead letters processed.
```
