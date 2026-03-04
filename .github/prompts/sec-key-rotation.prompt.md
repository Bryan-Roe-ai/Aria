```prompt
---
agent: agent
description: "Implement secure API key rotation without downtime"
---
# API Key Rotation
## Task
Implement zero-downtime API key rotation.
## Requirements
1. Support dual-key overlap period. 2. Mark old key as deprecated, not immediately revoked.
3. Set overlap window (24-48 hours). 4. Notify key owners before expiry.
5. Log usage of deprecated keys.
## Constraints
- Both keys valid during overlap. Notify 7 days before rotation. Revoke old key after window.
## Success Criteria
- Rotation causes zero downtime. Notifications sent. Old key usage tracked.
```
