```prompt
---
agent: agent
description: "Write performance regression tests with timing assertions"
---
# Performance Regression Tests
## Task
Write performance regression tests with timing thresholds.
## Requirements
1. Measure execution time for critical operations.
2. Set baseline thresholds with tolerance margins.
3. Use `pytest-benchmark` for statistical timing.
4. Compare against stored baselines.
5. Alert on significant regressions.
## Constraints
- Use warm-up iterations before measurement.
- Run on consistent hardware for reliable baselines.
- Allow 10-20% tolerance for natural variation.
## Success Criteria
- Performance regressions detected automatically.
- Baselines are stored and version-controlled.
- False positives minimized with tolerance.
```
