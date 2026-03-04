```prompt
---
agent: agent
description: "Implement API request correlation and distributed tracing"
---
# API Distributed Tracing
## Task
Implement request correlation and distributed tracing.
## Requirements
1. Generate or propagate `X-Request-ID` header. 2. Pass correlation ID through service calls.
3. Include correlation ID in all log entries. 4. Support W3C Trace Context headers.
5. Report trace spans to tracing backend.
## Constraints
- Always propagate existing IDs. Generate UUID v4 if missing. Include in error responses.
## Success Criteria
- Every request has correlation ID. ID propagated across services. Logs correlated.
```
