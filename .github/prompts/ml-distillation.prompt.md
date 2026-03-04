```prompt
---
agent: agent
description: "Implement model distillation for deployment efficiency"
---
# Model Distillation
## Task
Distill a large model into a smaller student model.
## Requirements
1. Train student model on teacher predictions (soft labels). 2. Use temperature scaling for knowledge transfer.
3. Compare student vs teacher accuracy. 4. Benchmark student inference speed.
5. Deploy student model for production.
## Constraints
- Student should be 10x+ smaller. Accept < 5% accuracy loss. Temperature 2-4 for distillation.
## Success Criteria
- Student model significantly smaller. Accuracy close to teacher. Inference faster.
```
