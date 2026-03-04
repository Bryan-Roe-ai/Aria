```prompt
---
agent: agent
description: "Implement API graceful shutdown with connection draining"
---
# API Graceful Shutdown
## Task
Implement graceful shutdown for API servers.
## Requirements
1. Stop accepting new connections on SIGTERM. 2. Drain existing connections (max 30s).
3. Complete in-flight requests. 4. Close database connections and cleanup.
5. Return 503 for new requests during shutdown.
## Constraints
- Shutdown timeout 30s max. Log shutdown progress. Exit 0 on clean shutdown.
## Success Criteria
- In-flight requests complete. New requests rejected. Resources cleaned up. Clean exit.
```
