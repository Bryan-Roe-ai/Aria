```prompt
---
agent: agent
description: "Implement two-factor authentication (2FA/MFA)"
---
# Two-Factor Authentication
## Task
Implement 2FA/MFA for account security.
## Requirements
1. Support TOTP (Google Authenticator). 2. Support SMS fallback. 3. Generate and store backup codes.
4. Enforce 2FA for admin accounts. 5. Provide QR code for TOTP setup.
## Constraints
- SMS is fallback only. TOTP preferred. Store TOTP secrets encrypted. Rate-limit verification attempts.
## Success Criteria
- 2FA enrollable and enforced. TOTP + backup codes work. Admin accounts require 2FA.
```
