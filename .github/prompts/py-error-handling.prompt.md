```prompt
---
agent: agent
description: "Add comprehensive error handling with custom exception hierarchy"
---
# Error Handling

## Task
Add structured error handling with a custom exception hierarchy.

## Requirements
1. Define a base exception class for the module.
2. Create specific exception subclasses for domain errors.
3. Add try/except blocks with appropriate granularity.
4. Include error context (original exception, parameters, timestamps).
5. Log errors with structured metadata before re-raising.

## Constraints
- Never catch and silently swallow exceptions.
- Use `raise ... from e` to preserve exception chains.
- Keep exception messages actionable and user-facing.

## Success Criteria
- All failure modes have specific exception types.
- Error messages include enough context for debugging.
- Exception hierarchy is documented in module docstring.
```
