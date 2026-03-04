```prompt
---
agent: agent
description: "Design RESTful API endpoints following best practices"
---
# REST API Design
## Task
Design RESTful API endpoints following HTTP standards.
## Requirements
1. Use proper HTTP methods (GET read, POST create, PUT replace, PATCH update, DELETE remove).
2. Use plural nouns for resource URLs (`/api/users`, not `/api/user`).
3. Return appropriate status codes (201 Created, 204 No Content, 404 Not Found).
4. Support pagination with `?page=1&limit=20` or cursor-based.
5. Include HATEOAS links for discoverability.
## Constraints
- Follow Aria `/api/` prefix convention. Use consistent error response schema.
## Success Criteria
- Endpoints are intuitive. Status codes correct. Pagination works. Errors are structured.
```
