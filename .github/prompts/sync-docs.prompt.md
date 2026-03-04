```prompt
---
agent: agent
---
Task: Detect and reconcile documentation and metadata drift.

Requirements:
- Compare docs against current code/workflow/config behavior.
- Fix stale paths, counts, and references.
- Update folder indexes and cross-links.
- Keep one source of truth for duplicated guidance.

Constraints:
- Preserve valid historical context where needed.
- Avoid rewriting unrelated sections.

Success Criteria:
- No stale links or contradictory guidance remain in scope.
- Updated docs reflect actual repository behavior.
- Changes are concise and verifiable.
```
