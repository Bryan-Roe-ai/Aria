```prompt
---
agent: agent
description: "Implement secure inter-service communication"
---
# Secure Service Communication
## Task
Secure inter-service communication.
## Requirements
1. Use mutual TLS (mTLS) between services. 2. Implement service identity verification.
3. Encrypt all internal traffic. 4. Use service mesh for policy enforcement.
5. Rotate service certificates automatically.
## Constraints
- Zero trust: authenticate every service call. No plaintext internal traffic. Auto-rotate certs.
## Success Criteria
- mTLS between all services. Identity verified. Traffic encrypted. Certs rotated.
```
