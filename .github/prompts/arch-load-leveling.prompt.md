```prompt
---
agent: agent
description: "Implement queue-based load leveling"
---
# Queue-Based Load Leveling
## Task
Implement queue-based load leveling for traffic spikes.
## Requirements
1. Buffer requests in queue during spikes. 2. Process at sustainable rate.
3. Monitor queue depth. 4. Scale consumers based on depth.
5. Handle queue overflow with backpressure.
## Constraints
- Queue must be durable. Monitor depth and processing rate. Alert on high depth.
## Success Criteria
- Spikes buffered smoothly. Processing rate steady. No dropped requests.
```
