```prompt
---
agent: agent
description: "Implement mutation testing to verify test suite quality"
---
# Mutation Testing
## Task
Run mutation testing to verify test suite strength.
## Requirements
1. Set up `mutmut` or similar mutation testing tool.
2. Run mutations against the test suite.
3. Analyze surviving mutants (tests that missed bugs).
4. Add tests to kill surviving mutants.
5. Track mutation score over time.
## Constraints
- Mutation testing is slow; run on critical modules only.
- Not all mutations are meaningful; triage survivors.
- Use `--paths-to-mutate` to focus on important code.
## Success Criteria
- Mutation score exceeds target threshold.
- Surviving mutants are triaged and addressed.
- Test suite effectively catches code changes.
```
