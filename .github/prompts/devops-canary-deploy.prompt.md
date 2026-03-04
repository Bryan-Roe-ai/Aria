```prompt
---
agent: agent
description: "Implement canary deployment with progressive rollout"
---
# Canary Deployment
## Task
Implement canary deployment with progressive traffic shift.
## Requirements
1. Route 5% → 25% → 50% → 100% of traffic. 2. Monitor error rates at each stage.
3. Automatic rollback on error spike. 4. Wait for metrics stability between stages.
5. Support manual promotion gates.
## Constraints
- Error threshold for rollback: > 1% increase. Wait 5 min between stages. Monitor key metrics.
## Success Criteria
- Progressive rollout works. Errors trigger rollback. Full promotion succeeds.
```
