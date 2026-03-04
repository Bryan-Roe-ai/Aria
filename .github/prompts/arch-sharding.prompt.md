```prompt
---
agent: agent
description: "Implement sharding strategy for horizontal database scaling"
---
# Database Sharding
## Task
Implement sharding for horizontal database scalability.
## Requirements
1. Choose sharding key (user ID, tenant, region). 2. Implement consistent hashing for shard selection.
3. Handle cross-shard queries. 4. Support shard rebalancing.
5. Monitor shard hotspots.
## Constraints
- Sharding key immutable. Minimize cross-shard queries. Rebalance without downtime.
## Success Criteria
- Data distributed evenly. Hotspots detected. Rebalancing works without downtime.
```
