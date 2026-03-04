```chatagent
---
name: dashboard-and-monitoring
description: Training dashboard, GPU monitoring, WebSocket live progress, and analytics for Aria's observability surfaces.
---

# Dashboard & Monitoring Agent

## When to Use

- Modifying `dashboard/app.py` (Flask routes, SocketIO events).
- Adding dashboard pages or widgets in `dashboard/templates/`.
- WebSocket/live-progress changes (`websocket_server.py`, `live-progress.js`).
- GPU monitoring (`gpu_monitor.py`) or resource observation scripts.
- Anomaly detection or model comparison UI features.

## Workflow

1. **Read status** — Dashboard reads from `data_out/<orchestrator>/status.json`; understand the data shape first.
2. **Inspect** — Read `dashboard/app.py`, relevant templates, and JS helpers.
3. **Implement** — Flask routes return JSON for `/status`, `/metrics`, `/health`; HTML templates are for human dashboards.
4. **Push updates** — Use SocketIO `emit` for live data; avoid polling in Python threads.
5. **Test** — Verify routes return valid JSON, templates render without errors, and WebSocket connections establish.

## Guardrails

- Dashboard is read-only for orchestrator state; never write to `data_out/` from dashboard code.
- Do not embed secrets in templates; pass safe display values from the server.
- Keep JS helpers single-purpose and free of bundler dependencies.
- Ensure all interactive elements are keyboard-accessible with ARIA labels.
- GPU monitoring: handle missing `nvidia-smi` gracefully; not all hosts have GPUs.
```
