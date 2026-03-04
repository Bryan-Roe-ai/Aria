```prompt
---
agent: agent
description: "Define abstract base classes for interface contracts"
---
# ABC Interface

## Task
Define abstract base classes for explicit interface contracts.

## Requirements
1. Create ABC with `@abstractmethod` for required methods.
2. Add `@abstractproperty` for required properties.
3. Use `register()` for virtual subclass registration.
4. Document the contract each method must fulfill.
5. Add default implementations for optional methods.

## Constraints
- Prefer Protocol over ABC for structural typing.
- Use ABC when runtime isinstance checks are needed.
- Keep abstract methods minimal; add concrete helpers.

## Success Criteria
- Interface contracts are explicit and enforced.
- Non-implementing subclasses raise `TypeError` at instantiation.
- Documentation clearly describes each method's contract.
```
