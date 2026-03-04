```prompt
---
agent: agent
description: "Implement the observer/event pattern for loose coupling"
---
# Observer Pattern

## Task
Implement an event/observer system for decoupled communication.

## Requirements
1. Define an event emitter with subscribe/unsubscribe/emit methods.
2. Support typed event payloads.
3. Handle subscriber errors without crashing the emitter.
4. Support async subscribers if needed.
5. Add weak references to prevent memory leaks.

## Constraints
- Catch and log subscriber exceptions; don't propagate.
- Use `weakref` callbacks to auto-unsubscribe dead objects.
- Keep the event system lightweight.

## Success Criteria
- Components communicate through events without direct references.
- Subscriber failures don't crash the event system.
- No memory leaks from retained subscriber references.
```
