```prompt
---
agent: agent
description: "Implement the command pattern for undo/redo and action queuing"
---
# Command Pattern

## Task
Implement the command pattern for undoable operations and action queuing.

## Requirements
1. Define a Command interface with `execute()` and `undo()`.
2. Store command history for undo/redo support.
3. Support macro commands (composite of multiple commands).
4. Add serialization for persistent command logs.
5. Implement command queue for deferred execution.

## Constraints
- Commands must capture all state needed for undo.
- Keep command objects lightweight and serializable.
- Limit history size to prevent memory growth.

## Success Criteria
- Operations are undoable and redoable.
- Command history is bounded and serializable.
- Macro commands compose correctly.
```
