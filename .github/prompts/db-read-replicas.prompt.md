```prompt
---
agent: agent
description: "Implement read replica configuration for read scaling"
---
# Read Replicas
## Task
Configure read replicas for horizontal read scaling.
## Requirements
1. Set up primary-replica replication. 2. Route read queries to replicas.
3. Handle replication lag. 4. Failover strategy for primary failure.
5. Monitor replication health.
## Constraints
- Write to primary only. Accept replication lag for reads. Failover within 30s.
## Success Criteria
- Reads distributed to replicas. Replication healthy. Failover works. Lag monitored.
```
