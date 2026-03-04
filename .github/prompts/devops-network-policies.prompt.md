```prompt
---
agent: agent
description: "Implement network policies for container isolation"
---
# Network Policies
## Task
Define network policies for container network isolation.
## Requirements
1. Default deny all ingress and egress. 2. Allow specific service-to-service communication.
3. Allow external access only for edge services. 4. Restrict egress to necessary external endpoints.
5. Test policies with connectivity checks.
## Constraints
- Default deny. Explicit allow per service pair. Document allowed flows.
## Success Criteria
- Network isolated by default. Only allowed traffic flows. Policies documented and tested.
```
