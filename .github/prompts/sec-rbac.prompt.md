```prompt
---
agent: agent
description: "Implement RBAC with least-privilege principle"
---
# RBAC Authorization
## Task
Implement role-based access control with least privilege.
## Requirements
1. Define roles (admin, editor, viewer, service). 2. Map roles to permissions (read, write, delete, admin).
3. Enforce at API layer and database layer. 4. Support role hierarchy.
5. Log all authorization decisions.
## Constraints
- Default deny. Minimum necessary permissions. Review roles quarterly.
## Success Criteria
- Roles enforced at all layers. Default deny. Decisions logged. Least privilege applied.
```
