```prompt
---
agent: agent
description: "Build multi-stage Docker image for production"
---
# Multi-Stage Docker
## Task
Build an optimized multi-stage Docker image.
## Requirements
1. Use build stage for compilation/dependencies. 2. Use minimal runtime stage (distroless/alpine).
3. Cache dependency layers effectively. 4. Run as non-root user.
5. Set health check and metadata labels.
## Constraints
- Final image < 200MB. No build tools in runtime. Pin base image versions.
## Success Criteria
- Image size minimized. Layers cached. Non-root. Health check configured.
```
