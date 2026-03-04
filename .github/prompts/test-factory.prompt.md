```prompt
---
agent: agent
description: "Write test factories to simplify test object creation"
---
# Test Factories
## Task
Implement test factories for clean test data creation.
## Requirements
1. Create factory functions with sensible defaults.
2. Allow overriding specific fields per test.
3. Use `factory_boy` or custom builders.
4. Support nested object creation.
5. Generate unique values for ID fields.
## Constraints
- Factories must produce valid objects by default. Make overrides explicit.
## Success Criteria
- Test setup simplified. Reduce boilerplate. Default objects are valid.
```
