```prompt
---
agent: agent
description: "Implement Cosmos DB container design and partitioning"
---
# Cosmos DB Design
## Task
Design Cosmos DB containers with optimal partitioning.
## Requirements
1. Choose partition key for even distribution. 2. Design for single-partition queries.
3. Configure throughput (RU/s) based on workload. 4. Implement change feed for event processing.
5. Monitor RU consumption and throttling.
## Constraints
- Partition key immutable. Avoid cross-partition queries. Follow Aria Cosmos patterns.
## Success Criteria
- Even data distribution. Queries single-partition. RUs sized correctly. No throttling.
```
