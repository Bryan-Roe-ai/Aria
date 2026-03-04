```prompt
---
agent: agent
description: "Test authentication flows and token management"
---
# Auth Tests
## Task
Write tests for authentication flows and token management.
## Requirements
1. Test login with valid and invalid credentials.
2. Test token generation, validation, and expiration.
3. Test refresh token flow.
4. Test token revocation.
5. Test multi-factor authentication steps.
## Constraints
- Never use real credentials in tests. Mock auth providers. Test expiration with time mocking.
## Success Criteria
- Auth flows validated end-to-end. Token lifecycle covered. Invalid attempts rejected.
```
