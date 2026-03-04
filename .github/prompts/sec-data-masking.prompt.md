```prompt
---
agent: agent
description: "Implement PII data masking and anonymization"
---
# Data Masking
## Task
Implement PII data masking and anonymization.
## Requirements
1. Identify PII fields (email, phone, SSN, address). 2. Mask PII in logs (show last 4 chars only).
3. Anonymize data for non-production environments. 4. Implement field-level encryption for PII at rest.
5. Support GDPR right to erasure.
## Constraints
- Masking must be irreversible in logs. Anonymized data must not be re-identifiable. GDPR compliant.
## Success Criteria
- PII masked in all logs. Non-prod data anonymized. Erasure supported. GDPR compliant.
```
