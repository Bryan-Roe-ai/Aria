```prompt
---
agent: agent
description: "Implement secure memory handling to prevent leaks"
---
# Secure Memory Handling
## Task
Handle sensitive data in memory securely.
## Requirements
1. Zero out sensitive data after use. 2. Use secure string types where available.
3. Avoid swapping sensitive pages to disk. 4. Minimize sensitive data lifetime in memory.
5. Prevent sensitive data in core dumps.
## Constraints
- Python: use SecretStr from pydantic. Clear references. Avoid logging variable contents.
## Success Criteria
- Sensitive data zeroed after use. Minimal memory lifetime. No leaks to logs/dumps.
```
