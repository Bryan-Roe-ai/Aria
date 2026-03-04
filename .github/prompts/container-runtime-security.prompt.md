```prompt
---
agent: agent
description: Enforce secure runtime settings for containers and orchestrators.
---
Task:
Configure runtime controls and policy constraints.
Requirements:
Set read-only FS, dropped caps, seccomp/apparmor where available.
Constraints:
Do not disable required container functionality blindly.
Success Criteria:
Runtime posture is hardened and policy-compliant.
```
