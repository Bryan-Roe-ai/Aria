```prompt
---
agent: agent
description: "Implement container orchestration health management"
---
# Container Health Management
## Task
Configure container health management and self-healing.
## Requirements
1. Define liveness probes (is process alive?). 2. Define readiness probes (is service ready?).
3. Define startup probes (has service started?). 4. Configure restart policies.
5. Implement graceful shutdown handling.
## Constraints
- Separate liveness from readiness. Startup probe for slow-starting apps. Graceful shutdown 30s.
## Success Criteria
- Unhealthy containers restarted. Unready containers removed from traffic. Graceful shutdown works.
```
