```prompt
---
agent: agent
description: "Set up mock servers for external API testing"
---
# Mock Server Tests
## Task
Create mock servers for testing external API integrations.
## Requirements
1. Use `responses`, `httpretty`, or `aioresponses` for HTTP mocking.
2. Record real responses for mock replay.
3. Simulate error responses and timeouts.
4. Test retry logic with mock failure sequences.
5. Verify request headers and body sent to mock.
## Constraints
- Mock all external calls in unit tests. Use recorded responses for integration tests.
## Success Criteria
- External APIs fully mocked. Error scenarios tested. Request validation works.
```
