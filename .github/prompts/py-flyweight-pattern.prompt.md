```prompt
---
agent: agent
description: "Implement the flyweight pattern for memory-efficient shared objects"
---
# Flyweight Pattern
## Task
Implement flyweight for memory-efficient shared object instances.
## Requirements
1. Identify intrinsic (shared) vs extrinsic (unique) state.
2. Create a flyweight factory that caches shared instances.
3. Pass extrinsic state as method parameters.
4. Measure memory savings from sharing.
5. Make flyweight objects immutable.
## Constraints
- Flyweight objects must be immutable (shared safely).
- Factory must handle concurrent access if multi-threaded.
- Only use when there are many similar objects.
## Success Criteria
- Memory usage reduced by sharing common state.
- Immutability prevents shared state corruption.
- Factory correctly deduplicates instances.
```
