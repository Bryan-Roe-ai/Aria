```prompt
---
agent: agent
description: "Implement ML pipeline with DAG orchestration"
---
# ML Pipeline Orchestration
## Task
Build ML pipeline with DAG-based orchestration.
## Requirements
1. Define pipeline stages (extract, transform, train, evaluate, deploy). 2. Implement dependency management between stages.
3. Support parallel execution where possible. 4. Handle failures with retry and alerting.
5. Log pipeline execution metrics.
## Constraints
- Idempotent stages. Artifact passing between stages. Failure isolation.
## Success Criteria
- Pipeline executes end-to-end. Failures contained. Parallel where possible. Reproducible.
```
