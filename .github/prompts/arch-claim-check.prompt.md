```prompt
---
agent: agent
description: "Implement claim check pattern for large message handling"
---
# Claim Check Pattern
## Task
Implement claim check for large message handling.
## Requirements
1. Store large payload in external storage. 2. Send claim token (reference) in message.
3. Consumer retrieves payload using claim. 4. Clean up stored payload after processing.
5. Handle expired claims.
## Constraints
- Payload size limit triggers claim check (> 256KB). Storage TTL matches SLA. Clean up after use.
## Success Criteria
- Large payloads handled without queue size issues. Claims resolve correctly. Cleanup works.
```
