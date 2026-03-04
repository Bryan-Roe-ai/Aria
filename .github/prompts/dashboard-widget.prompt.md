```prompt
---
agent: agent
description: "Add a new dashboard page, widget, or WebSocket event"
---
# Dashboard Widget

## Task
Add a new monitoring widget, page, or live-data feed to the dashboard.

## Context
- Flask app: `dashboard/app.py` (routes, SocketIO)
- Templates: `dashboard/templates/`
- JS helpers: `dashboard/*.js` (live-progress, anomaly-detector, model-comparator, etc.)
- WebSocket server: `dashboard/websocket_server.py`
- Data source: orchestrator status files in `data_out/<orchestrator>/status.json`

## Requirements
1. Add a Flask route or SocketIO event in `app.py`.
2. Create or update the HTML template with the widget markup.
3. If live data is needed, use SocketIO `emit` — not polling loops.
4. Ensure the route returns JSON for programmatic consumers.
5. Make the widget keyboard-accessible with ARIA labels.

## Constraints
- Dashboard is read-only for orchestrator state; never write to `data_out/`.
- Do not embed secrets in templates.
- No new CDN dependencies without justification.

## Success Criteria
- Widget renders correctly in the dashboard.
- SocketIO events fire and update the UI in real-time.
- Route returns valid JSON for API consumers.
```
