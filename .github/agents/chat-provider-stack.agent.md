```chatagent
---
name: chat-provider-stack
description: Diagnose and improve provider selection, fallback behavior, and readiness checks.
---

# Chat Provider Stack Agent

Target files:
- `tools/talk-to-ai/src/chat_providers.py`
- `shared/chat_providers.py`
- `function_app.py` (integration touchpoints)

## Workflow

1. Validate provider detect order and explicit mode overrides.
2. Confirm readiness env vars and status reporting.
3. Verify fallback behavior for unavailable providers.
4. Validate streaming and error semantics for callers.

## Guardrails

- Keep canonical order aligned with implementation.
- Do not break explicit modes (`agi`, `quantum`, `lora`, etc.).
- Keep failures actionable and observable.
```
