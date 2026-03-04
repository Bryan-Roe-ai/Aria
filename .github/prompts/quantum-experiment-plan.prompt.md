```prompt
---
agent: agent
---
Task: Plan and execute a safe quantum experiment workflow.

Requirements:
- Define objective, circuit/data assumptions, and evaluation metrics.
- Run local simulation first, then Azure simulator if needed.
- Gate paid QPU execution behind explicit cost confirmation.
- Record status/results and reproducibility settings.

Constraints:
- Keep bounded defaults for shots/qubits.
- Do not run paid hardware jobs without explicit approval.

Success Criteria:
- Experiment is reproducible and well-documented.
- Cost/risk controls are respected.
- Results include clear interpretation and next steps.
```
