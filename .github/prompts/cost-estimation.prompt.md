```prompt
---
agent: agent
description: "Estimate compute, storage, or API costs before running expensive operations"
---
# Cost Estimation

## Task
Estimate the cost of a planned operation before execution.

## Context
- Quantum: local simulator (free) → Azure simulator → paid QPU
- Training: GPU hours based on VRAM, batch size, epochs, dataset size
- API: token-based pricing for Azure OpenAI / OpenAI calls
- Storage: Cosmos RU costs, SQL DTU costs, blob storage

## Requirements
1. Identify all cost-bearing resources for the planned operation.
2. Estimate duration / token count / RU consumption.
3. Calculate approximate cost using current pricing tiers.
4. Present cost breakdown with alternatives (e.g., simulator vs QPU).
5. Get explicit confirmation before exceeding any cost threshold.

## Constraints
- Default to free/local options when available.
- Quantum: always use local simulator first, then Azure simulator, then paid QPU only with explicit cost confirmation.
- Training: use `scripts/vram_calculator.py` to estimate GPU requirements.
- Never auto-approve expensive operations.

## Success Criteria
- Cost estimate is presented before execution.
- Cheaper alternatives are suggested where applicable.
- User confirms before any paid resource usage.
- Actual cost tracked against estimate after execution.
```
