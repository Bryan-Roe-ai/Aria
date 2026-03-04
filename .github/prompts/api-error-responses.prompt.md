```prompt
---
agent: agent
description: "Design consistent API error responses with error codes"
---
# API Error Responses
## Task
Design a consistent error response format for all API endpoints.
## Requirements
1. Define error schema: `{error: {code, message, details, trace_id}}`.
2. Map exceptions to HTTP status codes.
3. Include machine-readable error codes for client handling.
4. Provide human-readable messages for debugging.
5. Include request trace ID for log correlation.
## Constraints
- Never expose stack traces in production. Sanitize error messages. Include trace ID.
## Success Criteria
- Consistent error format across all endpoints. Errors are actionable. No info leaks.
```
