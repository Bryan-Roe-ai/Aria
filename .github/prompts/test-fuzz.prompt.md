```prompt
---
agent: agent
description: "Implement fuzz testing for security and robustness"
---
# Fuzz Testing
## Task
Implement fuzz testing for security and robustness.
## Requirements
1. Identify input surfaces (API endpoints, parsers, deserializers).
2. Set up fuzzer (AFL, atheris, or custom).
3. Generate random/mutated inputs.
4. Monitor for crashes, hangs, and memory issues.
5. Save crash-inducing inputs for regression tests.
## Constraints
- Run in isolated environment with resource limits.
- Set timeouts per fuzz iteration.
- Keep crash corpus in version control.
## Success Criteria
- No crashes on fuzzed inputs.
- Found issues fixed and regression-tested.
- Crash corpus maintained for CI.
```
