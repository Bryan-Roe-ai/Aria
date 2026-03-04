```prompt
---
agent: agent
description: "Implement the Protocol pattern for structural subtyping"
---
# Protocol Pattern

## Task
Define and implement Protocol classes for structural (duck) typing.

## Requirements
1. Define `Protocol` classes for interfaces used across modules.
2. Use `@runtime_checkable` where isinstance checks are needed.
3. Document expected methods and their contracts.
4. Replace ABC-based inheritance with Protocols where appropriate.
5. Add type hints using Protocol types for function parameters.

## Constraints
- Protocols define structure, not behavior; keep them minimal.
- Use `@runtime_checkable` sparingly (performance cost).
- Don't add non-abstract methods to Protocol classes.

## Success Criteria
- Interfaces are defined as Protocols with clear contracts.
- Type checker validates structural conformance.
- Modules are decoupled from concrete class dependencies.
```
