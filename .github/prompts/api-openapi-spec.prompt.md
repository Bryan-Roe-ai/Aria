```prompt
---
agent: agent
description: "Generate OpenAPI/Swagger specification for API documentation"
---
# OpenAPI Specification
## Task
Generate OpenAPI 3.x specification for API documentation.
## Requirements
1. Document all endpoints with paths, methods, and parameters.
2. Define request/response schemas with JSON Schema.
3. Include authentication schemes.
4. Add example requests and responses.
5. Document error responses for each endpoint.
## Constraints
- Keep spec in sync with implementation. Use components for reusable schemas.
## Success Criteria
- Spec covers all endpoints. Schemas match actual payloads. Examples are valid.
```
