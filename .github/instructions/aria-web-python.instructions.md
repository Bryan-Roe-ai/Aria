```instructions
---
name: "Aria-Web-Python"
description: "Guidance for web/aria_web Python runtime"
applyTo: "web/aria_web/**/*.py"
---
# Aria Runtime Web Server – Python

- Keep endpoint behavior stable for:
  - `/api/aria/state`
  - `/api/aria/command`
  - `/api/aria/object`
  - `/api/aria/execute`
  - `/api/aria/world`
- Preserve deterministic updates to mutable stage/world state.
- Avoid hidden side effects between requests; isolate state transitions.
- Add structured error payloads for command failures.
- Keep latency-sensitive handlers lightweight; avoid blocking calls in hot paths.
- Do not hardcode secrets or endpoints.
- When changing request/response shapes, update paired frontend logic and docs.
```
