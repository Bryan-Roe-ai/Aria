```prompt
---
agent: agent
description: "Implement API request timeout and cancellation"
---
# API Request Timeout
## Task
Implement request timeout and cancellation handling.
## Requirements
1. Set server-side request timeout (30s default). 2. Return 504 Gateway Timeout on timeout.
3. Cancel downstream operations on client disconnect. 4. Clean up resources on timeout.
5. Log timeout events for monitoring.
## Constraints
- Timeouts should be per-endpoint configurable. Always clean up on cancel.
## Success Criteria
- Requests timeout after configured duration. Resources cleaned up. Timeouts logged.
```
