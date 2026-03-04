```prompt
---
agent: agent
description: "Implement model caching and warm-up strategies"
---
# Model Caching
## Task
Implement model caching and warm-up for fast inference.
## Requirements
1. Cache model in memory after first load. 2. Implement warm-up with dummy inference on startup.
3. Handle model reload on updates. 4. Support multi-model caching with LRU eviction.
5. Monitor cache hit rate and memory usage.
## Constraints
- Warm-up before serving traffic. LRU for memory constraints. Health check after warm-up.
## Success Criteria
- First request fast (warm-up done). Cache effective. Memory managed.
```
