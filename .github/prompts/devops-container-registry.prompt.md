```prompt
---
agent: agent
description: "Implement container registry management"
---
# Container Registry
## Task
Set up and manage container image registry.
## Requirements
1. Configure registry (ACR, ECR, Docker Hub). 2. Implement image tagging strategy (semver + git SHA).
3. Set up vulnerability scanning on push. 4. Implement retention policies for old images.
5. Configure access control and authentication.
## Constraints
- Scan all images before deployment. Retain last 10 versions minimum. Use immutable tags.
## Success Criteria
- Images tagged and stored correctly. Scans run. Retention enforced. Access controlled.
```
