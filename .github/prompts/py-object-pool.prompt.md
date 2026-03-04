```prompt
---
agent: agent
description: "Implement object pooling for expensive resource reuse"
---
# Object Pool
## Task
Implement an object pool for reusing expensive resources.
## Requirements
1. Create a pool with configurable min/max size.
2. Support acquire/release with context manager.
3. Validate objects before returning to the pool.
4. Implement idle timeout and eviction policies.
5. Add health checks for pooled objects.
## Constraints
- Pool must be thread-safe.
- Set maximum pool size to prevent resource exhaustion.
- Evict unhealthy objects rather than returning them.
## Success Criteria
- Resources are reused efficiently.
- Pool handles concurrent access safely.
- Unhealthy resources are evicted automatically.
```
