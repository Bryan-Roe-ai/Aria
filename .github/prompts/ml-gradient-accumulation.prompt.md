```prompt
---
agent: agent
description: "Implement gradient accumulation for large batch training"
---
# Gradient Accumulation
## Task
Implement gradient accumulation for training with limited GPU memory.
## Requirements
1. Accumulate gradients over N micro-batches. 2. Scale learning rate with effective batch size.
3. Sync accumulation with logging and evaluation. 4. Handle mixed precision with accumulation.
5. Benchmark memory savings vs training time.
## Constraints
- Effective batch size = micro_batch × accumulation_steps × GPUs. Adjust LR proportionally.
## Success Criteria
- Large effective batch size achieved. Memory within GPU limits. Training matches full-batch quality.
```
