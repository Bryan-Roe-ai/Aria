```prompt
---
agent: agent
description: "Implement compensating transaction for undo operations"
---
# Compensating Transaction
## Task
Implement compensating transactions for reversible operations.
## Requirements
1. Define compensating action for each step. 2. Execute compensations in reverse order on failure.
3. Handle partial compensation failures. 4. Log compensation execution.
5. Support manual compensation for edge cases.
## Constraints
- Every action must have a compensation. Compensations must be idempotent. Log exhaustively.
## Success Criteria
- Failed operations cleanly reversed. Compensations idempotent. State consistent after undo.
```
