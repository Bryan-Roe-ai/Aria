```prompt
---
agent: agent
description: "Implement the facade pattern to simplify complex subsystem interfaces"
---
# Facade Pattern
## Task
Create a facade to simplify access to a complex subsystem.
## Requirements
1. Identify the complex subsystem and its common use cases.
2. Create a facade class with high-level methods.
3. Delegate to subsystem components internally.
4. Expose only what consumers need.
5. Keep the facade stateless where possible.
## Constraints
- Facade should simplify, not add behavior.
- Don't prevent direct subsystem access for advanced users.
- Keep the facade API stable even if internals change.
## Success Criteria
- Common use cases are accessible through simple facade methods.
- Subsystem complexity is hidden from typical consumers.
- Advanced users can still access underlying components.
```
