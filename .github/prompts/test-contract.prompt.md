```prompt
---
agent: agent
description: "Implement contract testing for API consumer-provider contracts"
---
# Contract Tests
## Task
Implement contract tests for API consumer-provider agreements.
## Requirements
1. Define contracts with request/response schemas.
2. Provider tests verify the API satisfies contracts.
3. Consumer tests verify expectations match contracts.
4. Handle contract versioning and evolution.
5. Automate contract verification in CI.
## Constraints
- Contracts are bilateral agreements; both sides must verify.
- Breaking changes require contract version bump.
- Keep contracts minimal; only what consumers need.
## Success Criteria
- Contracts verified on both consumer and provider sides.
- Breaking changes detected automatically.
- Contract evolution is backward-compatible.
```
