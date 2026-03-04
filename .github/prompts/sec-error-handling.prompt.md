```prompt
---
agent: agent
description: "Implement secure error handling without information leakage"
---
# Secure Error Handling
## Task
Implement error handling that prevents information leakage.
## Requirements
1. Return generic error messages to clients. 2. Log detailed errors server-side only.
3. Never expose stack traces, SQL errors, or system paths. 4. Use error codes for client-side handling.
5. Sanitize error messages in all environments.
## Constraints
- Even in dev mode, don't expose internals to API clients. Log trace ID for correlation.
## Success Criteria
- No information leakage in error responses. Errors logged server-side. Trace IDs returned.
```
