```prompt
---
agent: agent
description: "Implement secure API versioning and deprecation"
---
# Secure API Lifecycle
## Task
Manage API security through version lifecycle.
## Requirements
1. Patch security issues across all supported versions. 2. Drop support for versions with unfixable vulnerabilities.
3. Communicate security deprecations with urgency. 4. Force upgrade for critical security issues.
5. Maintain security changelog.
## Constraints
- Security patches within 24h for critical. Force upgrade after 30 days grace. Document all CVEs.
## Success Criteria
- Security patches applied to all versions. Forced upgrades executed. Changelog maintained.
```
