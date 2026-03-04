```prompt
---
agent: agent
description: "Implement secure code signing and artifact verification"
---
# Code Signing
## Task
Implement code signing and artifact verification.
## Requirements
1. Sign all release artifacts (binaries, packages, images). 2. Verify signatures before deployment.
3. Use hardware security modules for signing keys. 4. Implement signature chain of trust.
5. Publish public keys for verification.
## Constraints
- Signing keys in HSM only. Rotate annually. Revoke compromised keys immediately.
## Success Criteria
- All artifacts signed. Signatures verified before deploy. Keys secured in HSM.
```
