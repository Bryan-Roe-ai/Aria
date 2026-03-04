```prompt
---
agent: agent
description: "Implement model safety and guardrails"
---
# Model Safety
## Task
Implement safety guardrails for model outputs.
## Requirements
1. Filter harmful or inappropriate outputs. 2. Implement content classification.
3. Apply output length limits. 4. Detect and prevent jailbreak attempts.
5. Log safety events for review.
## Constraints
- Safety checks must not add significant latency. False positive rate < 1%. Log all flags.
## Success Criteria
- Harmful outputs filtered. Jailbreaks detected. Safety events logged. Low false positives.
```
