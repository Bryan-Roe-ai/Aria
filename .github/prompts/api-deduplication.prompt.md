```prompt
---
agent: agent
description: "Implement API request deduplication for at-most-once delivery"
---
# API Deduplication
## Task
Implement request deduplication for at-most-once semantics.
## Requirements
1. Hash request body + user + endpoint for fingerprint. 2. Check fingerprint cache before processing.
3. Return cached response for duplicates within window. 4. Set deduplication window (5 minutes).
5. Handle race conditions with distributed locking.
## Constraints
- Dedup window configurable. Use atomic cache operations. Don't dedup GETs.
## Success Criteria
- Duplicate requests detected and skipped. Cache window enforced. Race conditions safe.
```
