```prompt
---
agent: agent
description: "Implement dependency supply chain security"
---
# Supply Chain Security
## Task
Secure the software supply chain for dependencies.
## Requirements
1. Pin dependency versions with hash verification. 2. Use lock files (pip freeze, package-lock.json).
3. Scan for known vulnerabilities on every PR. 4. Audit new dependency additions.
5. Use private registry mirror for critical packages.
## Constraints
- Never use unpinned dependencies in production. Review new deps for security.
## Success Criteria
- Dependencies pinned and verified. CVEs scanned on PR. New deps reviewed.
```
