```prompt
---
agent: agent
description: "Implement secure data retention and deletion policies"
---
# Data Retention
## Task
Implement data retention and secure deletion policies.
## Requirements
1. Define retention periods per data category. 2. Automate data expiry and deletion.
3. Implement secure deletion (not just soft delete for PII). 4. Support legal hold on specific records.
5. Audit all deletions.
## Constraints
- GDPR: delete PII within 30 days of request. Audit all deletions. Legal hold overrides retention.
## Success Criteria
- Retention automated. PII deleted securely. Legal holds respected. Deletions audited.
```
