```prompt
---
agent: agent
description: "Implement the visitor pattern for operations on object structures"
---
# Visitor Pattern
## Task
Implement the visitor pattern for operations on heterogeneous object structures.
## Requirements
1. Define a Visitor interface with visit methods for each element type.
2. Add accept() to element classes.
3. Implement concrete visitors for different operations.
4. Support double-dispatch for type-safe operations.
5. Add type hints for all visitor methods.
## Constraints
- Keep element classes stable; add new visitors for new operations.
- Handle unknown element types gracefully.
## Success Criteria
- New operations added without modifying element classes.
- Type safety maintained through double-dispatch.
```
