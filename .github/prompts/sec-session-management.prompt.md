```prompt
---
agent: agent
description: "Implement session management with security best practices"
---
# Secure Session Management
## Task
Implement secure session management.
## Requirements
1. Generate cryptographically random session IDs. 2. Set secure, httpOnly, sameSite cookie flags.
3. Implement session timeout (idle + absolute). 4. Regenerate session ID on privilege change.
5. Support concurrent session limits.
## Constraints
- Session ID length >= 128 bits. Idle timeout 30 min. Absolute timeout 8 hours. SameSite=Strict.
## Success Criteria
- Sessions secure with proper flags. Timeouts enforced. IDs regenerated on auth change.
```
