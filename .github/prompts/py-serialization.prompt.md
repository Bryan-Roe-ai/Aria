```prompt
---
agent: agent
description: "Implement serialization and deserialization for data interchange"
---
# Serialization
## Task
Implement serialization/deserialization for JSON, YAML, or binary formats.
## Requirements
1. Define serializable models with to_dict/from_dict methods.
2. Handle complex types (datetime, enum, UUID, bytes).
3. Support multiple formats (JSON, YAML, MessagePack).
4. Add versioning for backward-compatible schema evolution.
5. Validate data during deserialization.
## Constraints
- Use standard library JSON for simple cases; orjson for performance.
- Never deserialize untrusted data with pickle.
- Handle missing and extra fields gracefully (forward compatibility).
## Success Criteria
- Round-trip serialization preserves all data.
- Schema versions coexist without breaking changes.
- Complex types serialize/deserialize correctly.
```
