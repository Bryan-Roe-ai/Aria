```prompt
---
agent: agent
description: "Implement database data masking for non-production environments"
---
# Database Data Masking
## Task
Mask sensitive data when copying to non-production environments.
## Requirements
1. Identify sensitive columns (PII, financial). 2. Apply consistent masking per data type.
3. Maintain referential integrity after masking. 4. Automate masking in data refresh pipeline.
5. Verify no sensitive data remains.
## Constraints
- Non-reversible masking. Maintain FK relationships. Automated, not manual.
## Success Criteria
- Sensitive data masked. Referential integrity preserved. Automation works. Verified clean.
```
