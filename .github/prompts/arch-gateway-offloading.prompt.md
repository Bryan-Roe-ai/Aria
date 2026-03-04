```prompt
---
agent: agent
description: "Implement gateway offloading pattern"
---
# Gateway Offloading
## Task
Offload cross-cutting concerns to API gateway.
## Requirements
1. TLS termination at gateway. 2. Authentication at gateway.
3. Rate limiting at gateway. 4. Request transformation at gateway.
5. Keep backend services simple.
## Constraints
- Gateway is single entry point. Don't duplicate logic in backends. Monitor gateway health.
## Success Criteria
- Cross-cutting handled at gateway. Backends simplified. Gateway monitored.
```
