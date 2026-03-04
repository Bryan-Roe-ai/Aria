```prompt
---
agent: agent
description: "Implement backends for frontends with GraphQL federation"
---
# GraphQL Federation
## Task
Implement GraphQL federation for unified API gateway.
## Requirements
1. Define subgraphs per domain service. 2. Compose into federated supergraph.
3. Route queries to appropriate subgraphs. 4. Handle cross-subgraph references.
5. Monitor query performance across subgraphs.
## Constraints
- Each subgraph independently deployable. Composition validates at build time.
## Success Criteria
- Unified GraphQL API from federated subgraphs. Cross-references resolved. Performance tracked.
```
