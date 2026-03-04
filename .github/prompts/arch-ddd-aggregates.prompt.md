```prompt
---
agent: agent
description: "Implement domain-driven design aggregates and entities"
---
# DDD Aggregates
## Task
Design domain-driven design aggregates.
## Requirements
1. Identify aggregate roots. 2. Define consistency boundaries.
3. Keep aggregates small. 4. Reference other aggregates by ID only.
5. Implement domain events for cross-aggregate communication.
## Constraints
- One transaction per aggregate. Reference by ID, not object. Events for cross-aggregate.
## Success Criteria
- Aggregates have clear boundaries. Consistency enforced. Cross-aggregate via events.
```
