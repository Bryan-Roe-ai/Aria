```prompt
---
agent: agent
description: "Implement data encryption at rest and in transit"
---
# Data Encryption
## Task
Implement data encryption at rest and in transit.
## Requirements
1. Encrypt data at rest with AES-256. 2. Use TLS 1.3 for data in transit.
3. Manage encryption keys with key vault. 4. Implement key rotation without data re-encryption.
5. Encrypt PII fields in database.
## Constraints
- Minimum TLS 1.2. AES-256-GCM for symmetric. RSA-2048+ or ECDSA for asymmetric. Rotate keys annually.
## Success Criteria
- Data encrypted at rest and in transit. Keys managed securely. Rotation works.
```
