```prompt
---
agent: agent
description: "Write tests for error handling and exception paths"
---
# Error Path Tests
## Task
Write tests specifically for error handling code paths.
## Requirements
1. Test that correct exceptions are raised for invalid inputs.
2. Verify error messages are descriptive and actionable.
3. Test exception chaining (`raise ... from ...`).
4. Test cleanup runs during exception handling.
5. Use `pytest.raises` with match patterns.
## Constraints
- Test each error path independently. Verify both exception type and message.
## Success Criteria
- All error paths are tested. Exception messages are verified. Cleanup runs properly.
```
