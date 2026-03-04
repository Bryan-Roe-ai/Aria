```prompt
---
agent: agent
description: "Add structured logging with log levels, correlation IDs, and JSON output"
---
# Structured Logging

## Task
Implement structured logging with correlation IDs and JSON formatting.

## Requirements
1. Use Python `logging` module with named loggers.
2. Add correlation ID propagation across function calls.
3. Configure JSON formatter for machine-readable output.
4. Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
5. Include contextual fields (timestamp, module, function, line).

## Constraints
- Never log PII, secrets, or full request/response bodies.
- Keep log volume reasonable; avoid DEBUG in production.
- Use `logger = logging.getLogger(__name__)` pattern.

## Success Criteria
- Logs are structured JSON with correlation IDs.
- Log levels are appropriate for each message.
- Sensitive data is masked or excluded.
```
