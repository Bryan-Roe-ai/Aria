```prompt
---
agent: agent
description: "Implement blue-green deployment strategy"
---
# Blue-Green Deployment
## Task
Implement blue-green deployment for zero-downtime releases.
## Requirements
1. Run two identical environments (blue/green). 2. Deploy new version to inactive environment.
3. Run smoke tests on new environment. 4. Switch traffic with load balancer.
5. Keep old environment for instant rollback.
## Constraints
- Database migrations must be backward-compatible. Both environments must pass health checks.
## Success Criteria
- Zero-downtime deployment. Instant rollback available. Smoke tests pass before switch.
```
