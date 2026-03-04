```prompt
---
agent: agent
description: "Implement model monitoring for drift detection"
---
# Model Monitoring
## Task
Monitor deployed models for data and concept drift.
## Requirements
1. Track prediction distribution over time. 2. Detect data drift with statistical tests (KS, PSI).
3. Monitor feature distributions. 4. Alert on significant drift.
5. Trigger retraining when drift exceeds threshold.
## Constraints
- Baseline from training data. Monitor daily. Alert on >0.1 PSI. Retrain on sustained drift.
## Success Criteria
- Drift detected early. Alerts triggered. Retraining automated. Performance maintained.
```
