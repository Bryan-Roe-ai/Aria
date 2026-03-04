```prompt
---
agent: agent
description: "Implement CQRS (Command Query Responsibility Segregation)"
---
# CQRS Pattern
## Task
Implement CQRS for separate read and write models.
## Requirements
1. Separate command (write) and query (read) models. 2. Optimize read model for query patterns.
3. Sync read model from write events. 4. Handle eventual consistency.
5. Implement command validation.
## Constraints
- Accept eventual consistency for reads. Optimize each model independently. Command ≠ Query.
## Success Criteria
- Read and write paths separate. Queries optimized. Eventual consistency handled.
```
