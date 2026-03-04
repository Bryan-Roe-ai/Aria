```chatagent
---
name: aria-runtime-debug
description: Debug and improve Aria character runtime state/command behavior.
---

# Aria Runtime Debug Agent

Use for `web/aria_web/server.py` and `web/aria_web/aria_controller.js` issues.

## Workflow

1. Reproduce command/state issue.
2. Trace server state transitions and command mapping.
3. Patch with minimal behavior drift.
4. Validate endpoint parity and UI integration.

## Guardrails

- Keep state mutations deterministic.
- Preserve command synonym behavior unless intentionally changed.
- Update docs when endpoint payloads change.
```
