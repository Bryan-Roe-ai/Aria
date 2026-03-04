```prompt
---
agent: agent
description: "Implement auto-scaling for dynamic workloads"
---
# Auto-Scaling
## Task
Configure auto-scaling for dynamic workloads.
## Requirements
1. Define scaling metrics (CPU, memory, custom). 2. Set min/max replica counts.
3. Configure scale-up and scale-down policies. 4. Implement predictive scaling.
5. Test scaling behavior under load.
## Constraints
- Scale-up fast (30s), scale-down slow (5 min). Min replicas >= 2. Test with load generator.
## Success Criteria
- Scaling responds to load. Min replicas maintained. Scale-down gradual.
```
