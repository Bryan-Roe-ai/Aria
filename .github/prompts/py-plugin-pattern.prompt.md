```prompt
---
agent: agent
description: "Implement the plugin/extension pattern for runtime extensibility"
---
# Plugin Pattern

## Task
Implement a plugin system for runtime extensibility.

## Requirements
1. Define a plugin interface (Protocol) with lifecycle hooks.
2. Implement plugin discovery (entry points, directory scanning).
3. Add plugin registration and initialization order.
4. Support plugin dependencies and conflict detection.
5. Handle plugin load failures gracefully.

## Constraints
- Plugin loading must not crash the host application.
- Validate plugin interfaces at registration time.
- Support hot-reload where feasible.

## Success Criteria
- Plugins are discovered and loaded automatically.
- Failed plugins are isolated from the rest.
- Plugin lifecycle is documented and tested.
```
