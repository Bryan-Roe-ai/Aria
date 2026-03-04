```prompt
---
agent: agent
description: "Implement RLHF for model alignment"
---
# RLHF Alignment
## Task
Implement Reinforcement Learning from Human Feedback.
## Requirements
1. Collect human preference data (pairwise comparisons). 2. Train reward model on preferences.
3. Fine-tune policy with PPO against reward model. 4. Implement KL divergence constraint.
5. Evaluate alignment metrics.
## Constraints
- Quality preference data critical. KL penalty prevents degeneration. Evaluate safety.
## Success Criteria
- Reward model trained. Policy aligned with preferences. KL constrained. Safety maintained.
```
