```prompt
---
agent: agent
description: "Implement data validation with schema checking and sanitization"
---
# Data Validation
## Task
Add comprehensive data validation with schema checking and sanitization.
## Requirements
1. Define validation schemas using Pydantic or jsonschema.
2. Validate input data at system boundaries (API, file, database).
3. Sanitize string inputs (strip, normalize, escape).
4. Return structured validation errors with field-level detail.
5. Separate validation from business logic.
## Constraints
- Validate early; fail fast at system boundaries.
- Never trust external input; validate everything.
- Return all validation errors at once, not one at a time.
## Success Criteria
- All external input is validated before processing.
- Validation errors include field names and expected types.
- Sanitized data is safe for downstream processing.
```
