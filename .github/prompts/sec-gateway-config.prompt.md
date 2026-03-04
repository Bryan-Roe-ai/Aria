```prompt
---
agent: agent
description: "Implement secure API gateway configuration"
---
# Secure API Gateway
## Task
Configure API gateway with security controls.
## Requirements
1. Enforce authentication at gateway level. 2. Apply rate limiting per consumer.
3. Block malicious request patterns (WAF rules). 4. Terminate TLS at gateway.
5. Log all requests for audit.
## Constraints
- WAF in detection mode first, then prevention. Block known attack patterns. Log everything.
## Success Criteria
- Auth enforced at gateway. Malicious requests blocked. TLS terminated. All traffic logged.
```
