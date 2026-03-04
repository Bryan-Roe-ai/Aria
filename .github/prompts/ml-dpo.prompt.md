```prompt
---
agent: agent
description: "Implement DPO (Direct Preference Optimization) training"
---
# DPO Training
## Task
Implement Direct Preference Optimization for model alignment.
## Requirements
1. Prepare paired preference data (chosen/rejected). 2. Configure DPO training with beta parameter.
3. Use reference model for regularization. 4. Evaluate alignment improvement.
5. Compare against RLHF baseline.
## Constraints
- DPO simpler than RLHF (no reward model). Beta controls divergence. Quality data critical.
## Success Criteria
- Model aligned with preferences. Simpler than RLHF. Quality measured and improved.
```
