```prompt
---
agent: agent
description: "Write integration tests for testing component interactions"
---
# Integration Tests
## Task
Write integration tests that verify component interactions.
## Requirements
1. Test real interactions between 2+ components.
2. Use test databases or containers for external dependencies.
3. Verify data flows correctly across boundaries.
4. Test error propagation between components.
5. Clean up test data after each test.
## Constraints
- Integration tests are slower; keep the count focused.
- Use environment markers to skip when dependencies unavailable.
- Don't duplicate unit test coverage.
## Success Criteria
- Component interactions are verified end-to-end.
- Tests clean up after themselves.
- Failures clearly indicate which interaction broke.
```
