```instructions
---
name: "Dashboard-JS"
description: "Guidance for dashboard/ JavaScript UI helpers and WebSocket consumers"
applyTo: "dashboard/**/*.js"
---
# Dashboard – JavaScript

- Dashboard JS files are vanilla JS helpers loaded by the Flask templates (no bundler).
- Keep each file single-purpose: `live-progress.js` for WebSocket, `anomaly-detector.js` for anomaly logic, etc.
- WebSocket connection: connect to the SocketIO server at the dashboard origin; handle `connect`, `disconnect`, and domain events.
- Chart rendering: prefer lightweight libraries already in use; avoid adding new CDN dependencies without justification.
- Keyboard navigation (`keyboard-nav.js`): ensure all interactive dashboard elements are focusable and ARIA-labeled.
- Do not store secrets or tokens in JS; fetch them server-side via API calls.
- Use `const`/`let`; avoid `var`. Prefer `async/await` over raw `.then()` chains.
- Error handling: catch fetch/WebSocket errors gracefully and display user-visible status messages.
```
