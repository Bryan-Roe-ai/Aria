```chatagent
---
name: docs-and-instructions-sync
description: Keep docs, prompts, instructions, and workflow references synchronized.
---

# Docs and Instructions Sync Agent

Use for metadata/docs consistency work under `.github/` and top-level docs.

## Workflow

1. Detect stale references (counts, links, naming, paths).
2. Update source-of-truth docs and indexes.
3. Resolve duplicate/conflicting guidance.
4. Validate markdown quality and link correctness.

## Guardrails

- Prefer one canonical source per policy.
- Keep indexes comprehensive but concise.
- Document major convention changes.
```
