```prompt
---
agent: agent
description: "Implement property-based testing with Hypothesis for invariant verification"
---
# Property-Based Tests
## Task
Implement property-based testing with Hypothesis.
## Requirements
1. Identify properties/invariants that should hold for all inputs.
2. Define strategies for generating test inputs.
3. Test with `@given` decorator and Hypothesis strategies.
4. Handle counterexample shrinking for debugging.
5. Set `@settings` for database, deadline, max_examples.
## Constraints
- Properties should be mathematical invariants, not specific values.
- Set reasonable deadlines to avoid slow test runs.
- Use `@example` to pin important specific cases.
## Success Criteria
- Properties hold across all generated inputs.
- Counterexamples are minimal and debuggable.
- Tests cover input space beyond human imagination.
```
