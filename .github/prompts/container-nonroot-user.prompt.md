```prompt
---
agent: agent
description: Run containers as non-root with least privilege.
---
Task:
Update image and runtime to non-root execution model.
Requirements:
Set user/group, file permissions, and writable paths.
Constraints:
Avoid broad permission grants as shortcuts.
Success Criteria:
Workload runs correctly without root privileges.
```
