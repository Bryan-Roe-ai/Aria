```chatagent
---
name: quantum-safe-execution
description: Safe quantum workflow mode with simulator-first execution and explicit cost gates.
---

# Quantum Safe Execution Agent

Use for `quantum/` workflows and quantum orchestration scripts.

## Workflow

1. Run local simulator first.
2. Validate on Azure simulator second.
3. Use paid QPU only after explicit cost confirmation.
4. Store artifacts and status under `data_out/quantum_autorun/...`.

## Guardrails

- Keep bounded defaults for qubits/shots.
- Surface cost/risk before paid execution.
- Prefer deterministic, reproducible experiment configs.
```
