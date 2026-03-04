```prompt
---
agent: agent
description: "Implement certificate pinning and TLS configuration"
---
# TLS Configuration
## Task
Configure TLS settings and certificate management.
## Requirements
1. Enforce TLS 1.2 minimum, prefer TLS 1.3. 2. Configure strong cipher suites only.
3. Implement HSTS with long max-age. 4. Set up certificate monitoring and renewal.
5. Configure OCSP stapling.
## Constraints
- Disable SSLv3, TLS 1.0, TLS 1.1. No RC4 or DES ciphers. HSTS includeSubDomains.
## Success Criteria
- TLS 1.3 preferred. Weak ciphers disabled. HSTS enforced. Certs monitored.
```
