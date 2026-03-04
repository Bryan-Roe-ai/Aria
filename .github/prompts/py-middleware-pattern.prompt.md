```prompt
---
agent: agent
description: "Implement the middleware pattern for request/response processing pipelines"
---
# Middleware Pattern
## Task
Implement a middleware pipeline for extensible request/response processing.
## Requirements
1. Define middleware interface with a next-handler chain.
2. Implement concrete middleware (auth, logging, error handling, compression).
3. Support ordering and conditional middleware.
4. Handle async middleware for I/O operations.
5. Make middleware composable and testable in isolation.
## Constraints
- Middleware order matters; document and enforce it.
- Each middleware should handle one concern.
- Don't break the chain; always call next unless explicitly terminating.
## Success Criteria
- Request/response passes through the middleware pipeline.
- Middleware is composable and independently testable.
- Order is documented and enforced.
```
