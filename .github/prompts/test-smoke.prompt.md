```prompt
---
agent: agent
description: "Write smoke tests for critical path quick validation"
---
# Smoke Tests
## Task
Write smoke tests for quick critical path validation.
## Requirements
1. Test that the application starts without errors.
2. Verify critical endpoints respond with expected status codes.
3. Check database connectivity.
4. Validate core business operations work.
5. Keep total smoke test runtime under 60 seconds.
## Constraints
- Smoke tests must be fast and reliable.
- Don't duplicate integration test depth.
- Failures should indicate something is fundamentally broken.
## Success Criteria
- Application startup verified.
- Critical endpoints respond correctly.
- Total runtime under 60 seconds.
```
