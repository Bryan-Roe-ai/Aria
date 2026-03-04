```prompt
---
agent: agent
description: "Review code for correctness, security, performance, and convention compliance"
---
# Code Review

## Task
Perform a thorough code review of the specified changes.

## Context
- Conventions: `.github/copilot-instructions.md` and path-specific `.instructions.md` files
- Provider order: lmstudio → azure → openai → local (with explicit agi/quantum/lora modes)
- Key patterns: env vars for secrets, `datasets/` read-only, `data_out/` write-only, SSE streaming format

## Requirements
1. **Correctness** — Logic errors, edge cases, error handling, return values.
2. **Security** — Hardcoded secrets, SQL injection, unsanitized input, missing auth checks.
3. **Performance** — Uncompiled regex in loops, unnecessary allocations, missing caching.
4. **Conventions** — Provider order, config precedence, file organization, import patterns.
5. **Tests** — Adequate coverage for changed code; no test pollution.

## Constraints
- Check against path-specific instruction files for domain rules.
- Flag potential breaking changes explicitly.
- Suggest fixes, not just problems.

## Success Criteria
- All critical issues identified with suggested fixes.
- No secrets or PII in the diff.
- Performance regressions flagged with evidence.
- Conventions compliance verified.
```
