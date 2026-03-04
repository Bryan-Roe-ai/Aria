```prompt
---
agent: agent
description: "Implement outbox pattern for reliable event publishing"
---
# Outbox Pattern
## Task
Implement transactional outbox for reliable event publishing.
## Requirements
1. Write events to outbox table in same transaction as data change. 2. Publish events from outbox asynchronously.
3. Mark events as published. 4. Handle retries for failed publish.
5. Clean up old published events.
## Constraints
- Same transaction for data + outbox. At-least-once delivery. Consumers must be idempotent.
## Success Criteria
- Events published reliably. No lost events. Consumers handle duplicates.
```
