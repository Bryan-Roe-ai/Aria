```prompt
---
agent: agent
---
Task: Diagnose and fix streaming/SSE reliability issues.

Requirements:
- Reproduce streaming issue with concrete steps.
- Verify message framing, chunk parsing, and terminal sentinel behavior.
- Fix upstream/downstream handling with minimal protocol drift.
- Add tests or debug checks for recurrence prevention.

Constraints:
- Preserve expected SSE semantics.
- Avoid changing protocol shape without coordination.

Success Criteria:
- Stream is stable under normal and edge-case conditions.
- `[DONE]`/terminal behavior is correct and consistent.
- Client parsing remains compatible.
```
