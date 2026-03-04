```prompt
---
agent: agent
description: "Implement API key management for third-party access"
---
# API Key Management
## Task
Implement API key management for third-party consumers.
## Requirements
1. Generate unique API keys with prefix (`aria_`).
2. Hash keys for storage (never store plaintext).
3. Support key rotation with overlap period.
4. Associate keys with permissions and rate limits.
5. Support key revocation and expiry.
## Constraints
- Use cryptographically secure random generation. Hash with bcrypt or SHA-256+salt.
## Success Criteria
- Keys generated securely. Hashed in storage. Rotation works. Revocation immediate.
```
