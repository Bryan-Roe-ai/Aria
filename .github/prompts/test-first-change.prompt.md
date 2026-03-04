```prompt
---
agent: agent
---
Task: Implement a change using a test-first workflow.

Requirements:
- Write or update failing tests that define expected behavior.
- Implement minimal code changes to satisfy tests.
- Re-run focused and adjacent tests.
- Document what behavior was locked by tests.

Constraints:
- Keep tests deterministic and isolated.
- Avoid broad rewrites while stabilizing behavior.

Success Criteria:
- New/updated tests fail pre-change and pass post-change.
- Existing relevant tests remain green.
- Behavior change is clearly documented.
```
