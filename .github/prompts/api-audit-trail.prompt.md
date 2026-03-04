```prompt
---
agent: agent
description: "Implement API request logging and audit trail"
---
# API Audit Trail
## Task
Implement request logging and audit trail for API calls.
## Requirements
1. Log every request with method, path, user, timestamp.
2. Log response status code and duration.
3. Redact sensitive fields (passwords, tokens, PII).
4. Store audit records for compliance retention.
5. Support query by user, time range, and endpoint.
## Constraints
- Never log request bodies containing secrets. Rotate logs. Keep audit immutable.
## Success Criteria
- All requests logged. Sensitive data redacted. Audit queryable and immutable.
```
