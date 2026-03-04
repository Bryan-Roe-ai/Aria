```prompt
---
agent: agent
description: "Implement distributed locking for resource coordination"
---
# Distributed Locking
## Task
Implement distributed locking for shared resource coordination.
## Requirements
1. Acquire lock with timeout. 2. Auto-release lock on expiry.
3. Support lock renewal for long operations. 4. Handle lock contention gracefully.
5. Implement fencing tokens for safety.
## Constraints
- Lock TTL prevents deadlock. Fencing tokens prevent stale locks. Use Redis or ZooKeeper.
## Success Criteria
- Locks prevent concurrent access. TTL prevents deadlocks. Fencing tokens work.
```
