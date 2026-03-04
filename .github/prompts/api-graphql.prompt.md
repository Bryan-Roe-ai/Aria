```prompt
---
agent: agent
description: "Implement GraphQL API schema and resolvers"
---
# GraphQL API
## Task
Implement GraphQL API with schema-first design.
## Requirements
1. Define schema with types, queries, and mutations.
2. Implement resolvers with data loader pattern.
3. Handle N+1 query problem with batching.
4. Implement input validation on mutations.
5. Add query complexity limits and depth limits.
## Constraints
- Limit query depth to 5. Set complexity budget per query. Use DataLoader for batching.
## Success Criteria
- Schema covers domain. N+1 resolved with DataLoader. Complexity limits enforced.
```
