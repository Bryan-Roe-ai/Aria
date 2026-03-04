```prompt
---
agent: agent
description: "Test permissions and RBAC authorization rules"
---
# Permission Tests
## Task
Write tests for role-based access control and permissions.
## Requirements
1. Test each role can access allowed resources.
2. Test each role is denied from restricted resources.
3. Test permission inheritance and role hierarchy.
4. Test dynamic permission changes take effect.
5. Test cross-tenant isolation.
## Constraints
- Test all role/resource combinations. Use parameterized tests for coverage.
## Success Criteria
- RBAC rules enforced correctly. No unauthorized access. Cross-tenant isolated.
```
