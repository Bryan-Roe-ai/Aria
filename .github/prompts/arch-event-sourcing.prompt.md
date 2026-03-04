```prompt
---
agent: agent
description: "Implement event sourcing pattern for audit and replay"
---
# Event Sourcing
## Task
Implement event sourcing for full audit trail and replay.
## Requirements
1. Store all state changes as immutable events. 2. Rebuild state by replaying events.
3. Implement event store with append-only semantics. 4. Support snapshots for performance.
5. Implement projections for read models.
## Constraints
- Events are immutable. Snapshots every N events. Version events for schema evolution.
## Success Criteria
- State reconstructable from events. Snapshots accelerate reads. Events versioned.
```
