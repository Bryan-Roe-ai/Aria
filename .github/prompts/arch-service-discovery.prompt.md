```prompt
---
agent: agent
description: "Implement service discovery for dynamic environments"
---
# Service Discovery
## Task
Implement service discovery for dynamic service locations.
## Requirements
1. Register services on startup. 2. Deregister on shutdown.
3. Health check registered services. 4. Client-side or server-side discovery.
5. Handle DNS-based and registry-based discovery.
## Constraints
- Health check every 10s. Deregister unhealthy after 30s. Support graceful deregistration.
## Success Criteria
- Services discoverable dynamically. Health checked. Unhealthy removed. Graceful lifecycle.
```
