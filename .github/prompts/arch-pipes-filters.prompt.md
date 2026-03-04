```prompt
---
agent: agent
description: "Implement pipes and filters architecture"
---
# Pipes and Filters
## Task
Implement pipes and filters for data processing.
## Requirements
1. Define filters as independent processing units. 2. Connect filters via pipes (queues/streams).
3. Support parallel filter execution. 4. Handle backpressure.
5. Monitor throughput per filter.
## Constraints
- Filters are stateless and independent. Pipes handle buffering. Backpressure propagation.
## Success Criteria
- Data flows through filters. Parallel execution works. Backpressure handled.
```
