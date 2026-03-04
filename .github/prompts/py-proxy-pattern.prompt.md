```prompt
---
agent: agent
description: "Implement the proxy pattern for lazy loading, caching, or access control"
---
# Proxy Pattern

## Task
Implement a proxy for lazy loading, caching, or access control.

## Requirements
1. Define a proxy class with the same interface as the real subject.
2. Implement lazy initialization (create real subject on first access).
3. Add caching proxy for expensive operations.
4. Implement protection proxy for access control.
5. Make proxy transparent to the client.

## Constraints
- Proxy must fully implement the subject's interface.
- Handle lifecycle of the real subject correctly.
- Don't add unnecessary overhead for non-proxied operations.

## Success Criteria
- Proxy is transparent to consumers.
- Lazy loading defers creation until needed.
- Access control is enforced at the proxy level.
```
