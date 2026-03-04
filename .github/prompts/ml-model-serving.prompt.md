```prompt
---
agent: agent
description: "Implement model serving and inference optimization"
---
# Model Serving
## Task
Deploy model for efficient inference serving.
## Requirements
1. Select serving framework (FastAPI, TorchServe, vLLM). 2. Implement batched inference.
3. Configure model caching and warm-up. 4. Set up auto-scaling based on load.
5. Monitor inference latency and throughput.
## Constraints
- P95 latency target. Warm-up on startup. Batch for throughput. Health endpoint required.
## Success Criteria
- Model serving with target latency. Batching works. Auto-scaling configured. Monitored.
```
