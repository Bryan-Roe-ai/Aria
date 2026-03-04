```prompt
---
agent: agent
description: "Implement health endpoint monitoring pattern"
---
# Health Endpoint Monitoring
## Task
Implement health endpoint monitoring for services.
## Requirements
1. Expose /health for liveness (am I running?). 2. Expose /ready for readiness (can I serve?).
3. Check dependencies in readiness (DB, cache, external). 4. Structured response with component status.
5. Support degraded state (partially healthy).
## Constraints
- Health check fast (< 1s). Don't expose sensitive info. Follow Aria /api/ai/status pattern.
## Success Criteria
- Health accurately reflects state. Dependencies checked. Degraded state reported.
```
