```prompt
---
agent: agent
description: "Implement secure webhook signature verification"
---
# Webhook Signature Verification
## Task
Implement webhook payload signature verification.
## Requirements
1. Compute HMAC-SHA256 of payload with shared secret. 2. Compare computed signature with header value.
3. Use timing-safe comparison. 4. Reject requests with missing/invalid signatures.
5. Support signature version rotation.
## Constraints
- Timing-safe compare mandatory. Reject on any mismatch. Log verification failures.
## Success Criteria
- Signatures verified on every webhook. Timing-safe. Rotation supported.
```
