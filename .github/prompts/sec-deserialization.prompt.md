```prompt
---
agent: agent
description: "Implement secure deserialization practices"
---
# Secure Deserialization
## Task
Implement safe deserialization of untrusted data.
## Requirements
1. Never use pickle for untrusted input. 2. Validate JSON schema before processing.
3. Set size limits on deserialized objects. 4. Use safe YAML loading (yaml.safe_load).
5. Validate types after deserialization.
## Constraints
- Deny by default: reject unknown fields. Size limits mandatory. No eval-based deserialization.
## Success Criteria
- Untrusted data safely deserialized. No code execution. Size limits enforced.
```
