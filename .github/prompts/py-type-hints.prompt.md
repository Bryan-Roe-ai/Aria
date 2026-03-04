```prompt
---
agent: agent
description: "Add Python type hints and mypy-compatible annotations throughout a module"
---
# Type Hints

## Task
Add comprehensive type hints and annotations to a Python module.

## Requirements
1. Add parameter and return type annotations to all functions.
2. Use `typing` module for complex types (Optional, Union, Dict, List, Tuple).
3. Add type aliases for frequently used complex types.
4. Use `TypeVar` and `Generic` for generic classes.
5. Ensure compatibility with mypy strict mode.

## Constraints
- Use `from __future__ import annotations` for forward references.
- Prefer `X | Y` syntax (Python 3.10+) over `Union[X, Y]` where supported.
- Don't use `Any` as an escape hatch; be specific.

## Success Criteria
- All public functions have complete type annotations.
- `mypy --strict` passes without errors.
- Complex types have readable aliases.
```
