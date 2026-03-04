```chatagent
---
name: functions-api
description: Focused mode for implementing and validating Azure Functions API changes in Aria.
---

# Functions API Agent

Use this mode when editing `function_app.py` and related API behavior.

## Workflow

1. Identify endpoint scope and expected request/response contract.
2. Implement smallest safe change.
3. Validate streaming behavior (if applicable) and `/api/ai/status` diagnostics.
4. Add/update tests and docs for changed endpoints.

## Guardrails

- Preserve SSE format (`data: {json}` chunks + `data: [DONE]`).
- Never hardcode secrets; use env/config.
- Prefer shared modules over duplicate route-local logic.
- Treat diagnostics from `/api/ai/status` as source of truth.
```
