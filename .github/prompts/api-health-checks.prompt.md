```prompt
---
agent: agent
description: "Implement API health checks and readiness probes"
---
# API Health Checks
## Task
Implement health check and readiness probe endpoints.
## Requirements
1. Create `/health` endpoint for liveness (always 200 if running).
2. Create `/ready` endpoint checking dependencies (DB, cache, external).
3. Return structured health response with component status.
4. Support degraded status (partial failures).
5. Follow Aria `/api/ai/status` pattern for diagnostics.
## Constraints
- Health checks must be fast (< 1s). Don't include sensitive data. Support K8s probes.
## Success Criteria
- Health endpoint always responds. Readiness reflects dependency state. Response is structured.
```
