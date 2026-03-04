```instructions
---
name: "Quantum-Web-UI"
description: "Guidance for quantum/ web dashboard and visualization UI"
applyTo: "quantum/web_ui/**"
---
# Quantum Web UI

- `quantum/web_ui/` hosts the quantum experiment dashboard: `index.html` and `static/` assets.
- `quantum/web_app.py` is the Flask server backing this UI.
- Display experiment results, circuit visualizations, and training progress.
- Keep the UI lightweight; minimize CDN dependencies.
- Data flows from `quantum/results/` or backend API; the UI is read-only for results.
- Ensure keyboard accessibility and ARIA labels on interactive elements.
- Do not embed API keys or quantum credentials in client-side code.
- Handle missing data gracefully (e.g., no results yet? show a friendly empty state).
```
