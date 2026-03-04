```prompt
---
agent: agent
description: "Test canary deployment validation and rollback"
---
# Canary Tests
## Task
Write tests for canary deployment validation logic.
## Requirements
1. Test canary traffic splitting (percentage-based).
2. Test health check monitoring during canary.
3. Test automatic rollback on error threshold.
4. Test promotion from canary to full deployment.
5. Test metrics comparison between canary and baseline.
## Constraints
- Canary tests validate deployment logic, not infrastructure. Mock metrics APIs.
## Success Criteria
- Traffic splitting verified. Rollback triggers on errors. Promotion works cleanly.
```
