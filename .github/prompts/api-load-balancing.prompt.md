```prompt
---
agent: agent
description: "Implement API load balancing configuration"
---
# API Load Balancing
## Task
Configure load balancing for API high availability.
## Requirements
1. Distribute traffic across multiple instances. 2. Support round-robin and least-connections algorithms.
3. Implement health check for backend instances. 4. Handle sticky sessions when needed.
5. Support graceful shutdown with connection draining.
## Constraints
- Health checks every 10s. Remove unhealthy instances within 30s. Drain connections on shutdown.
## Success Criteria
- Traffic distributed evenly. Unhealthy instances removed. Graceful shutdown works.
```
