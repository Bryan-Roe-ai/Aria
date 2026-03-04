```prompt
---
agent: agent
description: "Implement GPU memory optimization for training"
---
# GPU Memory Optimization
## Task
Optimize GPU memory usage for model training.
## Requirements
1. Profile memory usage per layer. 2. Implement gradient checkpointing.
3. Use DeepSpeed ZeRO stages. 4. Optimize batch size vs memory tradeoff.
5. Handle multi-GPU memory distribution.
## Constraints
- Monitor OOM risk. Use gradient checkpointing before reducing batch size. Profile first.
## Success Criteria
- Memory usage minimized. Larger models/batches fit. No OOM errors.
```
