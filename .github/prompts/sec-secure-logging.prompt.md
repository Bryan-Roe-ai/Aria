```prompt
---
agent: agent
description: "Implement secure logging without sensitive data exposure"
---
# Secure Logging
## Task
Implement logging that excludes sensitive data.
## Requirements
1. Redact passwords, tokens, and API keys from logs. 2. Mask PII fields (email, phone, SSN).
3. Use structured logging with safe field serialization. 4. Prevent log injection attacks.
5. Set log retention and rotation policies.
## Constraints
- Never log raw request bodies containing credentials. Sanitize before logging. Encode special chars.
## Success Criteria
- No sensitive data in logs. Log injection prevented. Retention configured.
```
