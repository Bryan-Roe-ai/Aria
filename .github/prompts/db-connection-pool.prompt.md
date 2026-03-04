```prompt
---
agent: agent
description: "Implement database connection pooling configuration"
---
# Database Connection Pooling
## Task
Configure database connection pooling for optimal performance.
## Requirements
1. Set pool size based on workload (CPU cores * 2 + disk). 2. Configure connection timeout.
3. Set idle connection timeout. 4. Implement connection validation.
5. Monitor pool utilization.
## Constraints
- Don't over-provision connections. Validate on checkout. Idle timeout 5 min.
## Success Criteria
- Pool sized correctly. Connections healthy. No exhaustion under load.
```
