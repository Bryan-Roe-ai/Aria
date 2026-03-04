```prompt
---
agent: agent
description: "Implement sidecar pattern for cross-cutting concerns"
---
# Sidecar Pattern
## Task
Implement sidecar pattern for cross-cutting concerns.
## Requirements
1. Deploy sidecar alongside main service. 2. Handle logging, monitoring, and networking in sidecar.
3. Share lifecycle with main container. 4. Communicate over localhost.
5. Keep main service focused on business logic.
## Constraints
- Sidecar shares pod/host. Not for business logic. Low overhead communication.
## Success Criteria
- Cross-cutting concerns handled by sidecar. Main service simplified. Low overhead.
```
