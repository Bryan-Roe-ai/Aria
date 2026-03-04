```prompt
---
agent: agent
description: "Implement API request validation with schema enforcement"
---
# API Request Validation
## Task
Implement request validation with schema enforcement.
## Requirements
1. Validate request body against JSON Schema.
2. Validate query parameters (types, ranges, enums).
3. Validate path parameters (format, existence).
4. Return 422 Unprocessable Entity with field-level errors.
5. Support custom validators for business rules.
## Constraints
- Validate early, before business logic. Return all errors, not just first. Use pydantic or similar.
## Success Criteria
- Invalid requests rejected with clear errors. All fields validated. Business rules enforced.
```
