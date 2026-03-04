```prompt
---
agent: agent
---
Task: Diagnose provider selection and fallback behavior.

Requirements:
- Inspect configured providers, readiness checks, and detect order.
- Reproduce fallback path for unavailable providers.
- Patch incorrect detect/fallback behavior with minimal change.
- Confirm diagnostics and status endpoint outputs remain accurate.

Constraints:
- Preserve explicit provider mode overrides.
- Do not silently swallow provider failures.

Success Criteria:
- Correct provider selected in expected scenarios.
- Fallback path works and is observable.
- Documentation and status signals are aligned.
```
