```prompt
---
agent: agent
description: "Implement mixed precision training for GPU efficiency"
---
# Mixed Precision Training
## Task
Enable mixed precision training with FP16/BF16.
## Requirements
1. Use automatic mixed precision (AMP). 2. Identify operations that need FP32.
3. Implement gradient scaling to prevent underflow. 4. Benchmark speed and memory improvement.
5. Validate model quality matches FP32 training.
## Constraints
- BF16 preferred for stability if hardware supports it. Monitor for NaN/Inf. Gradient scaling required.
## Success Criteria
- Training 2x faster. Memory 50% reduced. Quality matches FP32. No NaN issues.
```
