```instructions
---
name: "Aria-Web-JS"
description: "Guidance for web/aria_web JavaScript runtime behavior"
applyTo: "web/aria_web/**/*.js"
---
# Aria Runtime Web – JavaScript

- Keep command synonym mapping and UX behavior backward-compatible.
- Favor explicit command parsing over fragile regex chains.
- Use small, composable handlers for stateful actions.
- Guard DOM access and asynchronous side effects.
- Keep animations/effects optional and non-blocking.
- Maintain parity with server-side command/state API contracts.
- For any new command, document expected payload and response behavior.
```
