```prompt
---
agent: agent
description: "Implement test data builders for readable test setup"
---
# Test Data Builders
## Task
Implement test data builders for clean, readable test setup.
## Requirements
1. Create builder classes with fluent API for test data.
2. Provide sensible defaults for all fields.
3. Allow selective overrides for test-specific values.
4. Support building related object graphs.
5. Use factory methods for common configurations.
## Constraints
- Builders should produce valid objects by default.
- Keep builder API minimal; don't expose every field.
- Builders are test utilities only; not for production code.
## Success Criteria
- Test setup is readable and focused on what matters.
- Default values produce valid objects.
- Related object graphs are consistent.
```
