```instructions
---
name: "Dashboard-Python"
description: "Guidance for dashboard/ Flask app, WebSocket server, and monitoring scripts"
applyTo: "dashboard/**/*.py"
---
# Dashboard – Python

- The dashboard is a Flask + SocketIO app (`dashboard/app.py`) that reads orchestrator status from `data_out/`.
- Templates live in `dashboard/templates/`; static JS helpers are adjacent to `app.py`.
- WebSocket server (`websocket_server.py`) pushes live training progress to connected dashboards.
- GPU monitor (`gpu_monitor.py`) and serve script (`serve.py`) are standalone utilities — keep them importable without Flask.
- Status aggregation: read `data_out/<orchestrator>/status.json` files; never write to them from the dashboard.
- Use `REPO_ROOT` path resolution (`Path(__file__).resolve().parents[1]`) for cross-module imports.
- All dashboard routes must return JSON from `/status`, `/metrics`, `/health` for programmatic consumers; HTML is for human-facing pages only.
- Prefer `flask_socketio.emit` for push updates; avoid polling loops in Python threads where WebSocket is available.
- Do not embed secrets in templates; use server-side env vars and pass safe display values only.
```
