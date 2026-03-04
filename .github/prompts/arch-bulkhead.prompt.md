```prompt
---
agent: agent
description: "Implement bulkhead pattern for fault isolation"
---
# Bulkhead Pattern
## Task
Implement bulkhead pattern to isolate failures.
## Requirements
1. Partition resources per service/component. 2. Set resource limits per partition (thread pools, connections).
3. Prevent one partition's failure from cascading. 4. Monitor partition utilization.
5. Alert when partitions near capacity.
## Constraints
- Each partition independently bounded. Don't share thread pools across services.
## Success Criteria
- Failures isolated to partitions. No cascade. Utilization monitored. Alerts configured.
```
