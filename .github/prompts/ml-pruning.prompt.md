```prompt
---
agent: agent
description: "Implement model pruning for efficiency"
---
# Model Pruning
## Task
Prune neural network for deployment efficiency.
## Requirements
1. Implement structured pruning (channels/heads). 2. Implement unstructured pruning (individual weights).
3. Evaluate accuracy vs sparsity tradeoff. 4. Fine-tune after pruning.
5. Benchmark pruned model inference.
## Constraints
- Target 50-90% sparsity. Fine-tune to recover accuracy. Test on target hardware.
## Success Criteria
- Model pruned to target sparsity. Accuracy recovered. Inference faster.
```
