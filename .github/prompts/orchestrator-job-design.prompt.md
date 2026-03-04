```prompt
---
agent: agent
---
Task: Design or enhance an orchestrator job with dry-run-safe behavior.

Requirements:
- Define job inputs, outputs, and status schema.
- Implement/verify dry-run path before real execution.
- Persist machine-readable status and artifact paths.
- Include failure handling and resumability guidance.

Constraints:
- Treat `datasets/` as immutable input.
- Persist generated outputs under `data_out/`.

Success Criteria:
- Dry-run validates configuration correctly.
- Job execution state is observable and machine-readable.
- Recovery paths are explicit and testable.
```
