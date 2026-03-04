```prompt
---
agent: agent
description: "Implement CI/CD pipeline with GitHub Actions"
---
# GitHub Actions CI/CD
## Task
Implement CI/CD pipeline using GitHub Actions.
## Requirements
1. Build and test on every PR. 2. Deploy to staging on merge to main.
3. Deploy to production with manual approval. 4. Cache dependencies for speed.
5. Run security scans in pipeline.
## Constraints
- Pin action versions by SHA. Use OIDC for cloud auth. Fail fast on lint/test errors.
## Success Criteria
- Pipeline runs on PR. Staging auto-deploys. Production requires approval. Security scanned.
```
