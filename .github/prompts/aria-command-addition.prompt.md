```prompt
---
agent: agent
description: "Add a new Aria runtime command or state transition"
---
# Aria Command Addition

## Task
Add a new command or state transition to the Aria character runtime.

## Context
- Server: `web/aria_web/server.py` (Flask, mutable `stage_state`)
- Controller: `web/aria_web/aria_controller.js` (client-side effects/commands)
- Endpoints: `/api/aria/state`, `/api/aria/command`, `/api/aria/object`, `/api/aria/execute`, `/api/aria/world`
- Frontend: `web/aria_web/index.html`

## Requirements
1. Define the new command name, parameters, and expected behavior.
2. Add server-side handler in `server.py` under the appropriate endpoint.
3. Add client-side effect in `aria_controller.js` if UI rendering needed.
4. Update `stage_state` transitions to be safe and reversible.
5. Add test coverage in `web/aria_web/test_auto_execute.py`.

## Constraints
- Keep commands idempotent where possible.
- Server state must be JSON-serializable for API consumers.
- No hardcoded secrets in the runtime.
- Client JS: use `const`/`let`, async/await, proper error handling.

## Success Criteria
- New command executes correctly via API.
- State transitions are consistent and queryable via `/api/aria/state`.
- Client-side rendering (if applicable) works without errors.
- Test coverage added for the new command.
```
