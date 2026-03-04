```prompt
---
agent: agent
description: "Implement API request/response transformation and mapping"
---
# API Data Transformation
## Task
Implement request/response data transformation layer.
## Requirements
1. Transform camelCase API fields to snake_case internal fields.
2. Map external DTOs to internal domain models.
3. Strip internal-only fields from responses.
4. Transform dates to ISO 8601 format.
5. Handle nested object transformation recursively.
## Constraints
- Keep transformation logic separate from business logic. Test round-trip correctness.
## Success Criteria
- API format and internal format differ cleanly. No internal fields leak. Dates consistent.
```
