```prompt
---
agent: agent
---
Task: Reproduce, isolate, and resolve a bug with a root-cause-first workflow.

Requirements:
- Reproduce the failure with explicit steps and expected vs actual behavior.
- Identify root cause before proposing fixes.
- Propose the smallest safe fix and likely side effects.
- Add or update regression coverage.

Constraints:
- Do not mask symptoms without addressing the root cause.
- Avoid unrelated refactors.
- Preserve public API behavior unless explicitly requested.

Success Criteria:
- Bug is reproducible before and resolved after the change.
- Regression test fails before and passes after fix.
- Risks and follow-up checks are documented.
```
