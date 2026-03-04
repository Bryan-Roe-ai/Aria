```prompt
---
agent: agent
description: "Test logging output and telemetry emission"
---
# Logging Tests
## Task
Write tests to verify logging output and telemetry.
## Requirements
1. Use `caplog` fixture in pytest to capture logs.
2. Verify log levels, messages, and structured fields.
3. Test that sensitive data is not logged.
4. Test telemetry event emission.
5. Verify log formatting and correlation IDs.
## Constraints
- Never assert on exact timestamps. Check structured fields. Verify no secrets leaked.
## Success Criteria
- Log messages verified at correct levels. Sensitive data excluded. Telemetry emitted.
```
