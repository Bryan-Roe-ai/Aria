```prompt
---
agent: agent
description: "Test data serialization and deserialization formats"
---
# Serialization Tests
## Task
Write tests for data serialization/deserialization.
## Requirements
1. Test JSON serialization with custom encoders.
2. Test edge cases (None, datetime, Decimal, bytes).
3. Test round-trip: serialize → deserialize → compare.
4. Test malformed input handling.
5. Test serialization performance for large payloads.
## Constraints
- Test all custom types explicitly. Verify round-trip equality. Handle encoding errors.
## Success Criteria
- All types serialize correctly. Round-trip is lossless. Malformed input raises errors.
```
