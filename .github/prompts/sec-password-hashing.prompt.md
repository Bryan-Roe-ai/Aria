```prompt
---
agent: agent
description: "Implement secure password hashing and storage"
---
# Secure Password Hashing
## Task
Implement secure password hashing and credential storage.
## Requirements
1. Use bcrypt or argon2id for password hashing. 2. Set work factor appropriate for current hardware.
3. Generate unique salt per password. 4. Implement timing-safe comparison.
5. Support hash migration when algorithm is upgraded.
## Constraints
- Never store plaintext passwords. Never use MD5/SHA1 for passwords. Work factor >= 12.
## Success Criteria
- Passwords hashed with strong algorithm. Salts unique. Comparison timing-safe.
```
