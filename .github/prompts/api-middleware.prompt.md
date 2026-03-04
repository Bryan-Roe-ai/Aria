```prompt
---
agent: agent
description: "Implement API middleware for cross-cutting concerns"
---
# API Middleware
## Task
Implement middleware for cross-cutting API concerns.
## Requirements
1. Create request logging middleware (method, path, duration).
2. Create authentication middleware (token validation).
3. Create CORS middleware with configurable origins.
4. Create request ID middleware for tracing.
5. Define middleware execution order.
## Constraints
- Middleware must be composable. Order matters (auth before business logic). Keep lightweight.
## Success Criteria
- Cross-cutting concerns separated from route handlers. Middleware chain works correctly.
```
