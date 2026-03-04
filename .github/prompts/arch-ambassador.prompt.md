```prompt
---
agent: agent
description: "Implement ambassador pattern for external service connectivity"
---
# Ambassador Pattern
## Task
Implement ambassador for managing external service connectivity.
## Requirements
1. Deploy ambassador proxy alongside service. 2. Handle retries and circuit breaking.
3. Implement connection pooling. 4. Add monitoring and logging.
5. Handle TLS and authentication.
## Constraints
- Ambassador handles infrastructure concerns. Main service handles business logic only.
## Success Criteria
- External connectivity managed by ambassador. Main service simplified. Retries handled.
```
