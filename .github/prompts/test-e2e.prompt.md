```prompt
---
agent: agent
description: "Write end-to-end tests for full user workflow verification"
---
# E2E Tests
## Task
Write end-to-end tests for full user workflow verification.
## Requirements
1. Test complete user workflows from input to output.
2. Use the real system (API server, database) in test mode.
3. Verify response codes, headers, and body content.
4. Test happy path and common error paths.
5. Set up and tear down test fixtures cleanly.
## Constraints
- E2E tests are expensive; cover only critical paths.
- Use test environment configs, not production.
- Set timeouts for all network operations.
## Success Criteria
- Critical user workflows pass end-to-end.
- Tests are reliable and not flaky.
- Test environment is isolated from production.
```
