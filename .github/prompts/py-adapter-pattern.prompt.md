```prompt
---
agent: agent
description: "Implement the adapter pattern to bridge incompatible interfaces"
---
# Adapter Pattern

## Task
Implement an adapter to bridge incompatible interfaces.

## Requirements
1. Identify the target interface and the adaptee.
2. Create an adapter class that wraps the adaptee.
3. Translate method calls from target to adaptee format.
4. Handle data format conversions transparently.
5. Add type hints matching the target interface.

## Constraints
- Keep adapter logic thin; it's a translator, not business logic.
- Use composition over inheritance for the adapter.
- Document which adaptee version is supported.

## Success Criteria
- Client code works with the target interface seamlessly.
- Adaptee changes are isolated to the adapter layer.
- Data conversions are lossless.
```
