```prompt
---
agent: agent
description: "Implement the state pattern for finite state machines"
---
# State Pattern

## Task
Implement a state machine using the state pattern.

## Requirements
1. Define a State base class with methods for each event.
2. Implement concrete states with transition logic.
3. Store current state in the context object.
4. Log state transitions for debugging.
5. Define valid transitions and reject invalid ones.

## Constraints
- State classes should be stateless; context holds all state.
- Validate transitions explicitly; don't allow arbitrary state changes.
- Keep state transition logic in state classes, not the context.

## Success Criteria
- State machine handles all events correctly.
- Invalid transitions are rejected with clear errors.
- State transition history is logged.
```
