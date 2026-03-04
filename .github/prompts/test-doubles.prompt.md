```prompt
---
agent: agent
description: "Write tests using test doubles: stubs, fakes, spies, and dummies"
---
# Test Doubles
## Task
Apply appropriate test doubles for isolated testing.
## Requirements
1. Use stubs for predetermined responses.
2. Use fakes for lightweight working implementations.
3. Use spies to verify interaction behavior.
4. Use dummies for satisfying parameter requirements.
5. Choose the simplest double that meets the need.
## Constraints
- Don't over-mock; prefer fakes for complex dependencies.
- Spies should verify behavior, not implementation details.
## Success Criteria
- Tests are isolated from real dependencies. Right type of double used for each case.
```
