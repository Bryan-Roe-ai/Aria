```prompt
---
agent: agent
description: "Implement template method pattern for algorithm skeleton with customizable steps"
---
# Template Method

## Task
Implement the template method pattern for algorithms with customizable steps.

## Requirements
1. Define a base class with the template method (algorithm skeleton).
2. Mark customizable steps as abstract methods.
3. Provide hook methods with default (no-op) implementations.
4. Implement concrete subclasses for each variant.
5. Document which steps are required vs optional.

## Constraints
- Template method should be final (not overridable).
- Keep the number of abstract steps manageable.
- Hooks should be optional with sensible defaults.

## Success Criteria
- Algorithm structure is consistent across variants.
- Customizable steps are clearly defined.
- New variants only need to implement abstract steps.
```
