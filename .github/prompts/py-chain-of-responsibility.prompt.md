```prompt
---
agent: agent
description: "Implement chain of responsibility for sequential handler processing"
---
# Chain of Responsibility

## Task
Implement a chain of responsibility for sequential handler processing.

## Requirements
1. Define a handler base class with `handle()` and `set_next()`.
2. Implement concrete handlers for each processing step.
3. Build the chain by linking handlers together.
4. Support both "pass along" and "handle and stop" semantics.
5. Add logging for which handler processed each request.

## Constraints
- Each handler should handle one concern only.
- Chain order must be explicit and documented.
- Handle the case where no handler can process a request.

## Success Criteria
- Requests are processed by the correct handler.
- Chain is extensible without modifying existing handlers.
- Unhandled requests are reported clearly.
```
