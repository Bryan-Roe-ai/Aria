```prompt
---
agent: agent
description: "Implement container image optimization"
---
# Container Image Optimization
## Task
Optimize container images for size and security.
## Requirements
1. Use multi-stage builds. 2. Minimize layers (combine RUN commands).
3. Use .dockerignore to exclude unnecessary files. 4. Choose appropriate base image.
5. Remove package manager caches.
## Constraints
- Target < 100MB for API images. No dev dependencies in final. Pin versions.
## Success Criteria
- Image size minimized. No unnecessary files. Layers optimized. Build cache effective.
```
