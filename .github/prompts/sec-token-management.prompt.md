```prompt
---
agent: agent
description: "Implement secure API token management"
---
# API Token Security
## Task
Implement secure API token lifecycle management.
## Requirements
1. Generate tokens with cryptographic randomness. 2. Hash tokens before storage.
3. Set expiration on all tokens. 4. Support token scoping (read-only, full-access).
5. Implement token revocation and rotation.
## Constraints
- Minimum 256-bit token entropy. Store only hashes. Never log tokens. Rotate on compromise.
## Success Criteria
- Tokens generated securely. Hashed in storage. Scoped appropriately. Revocable.
```
