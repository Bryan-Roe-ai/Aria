```prompt
---
agent: agent
description: "Implement container security hardening"
---
# Container Security
## Task
Harden container images and runtime security.
## Requirements
1. Use minimal base images (distroless/alpine). 2. Run as non-root user. 3. Set read-only filesystem.
4. Drop all capabilities, add back only needed. 5. Scan images in CI for CVEs.
## Constraints
- No root processes. No writable root filesystem. Pin base image digests.
## Success Criteria
- Containers run non-root. Minimal attack surface. CVE-free images. Capabilities dropped.
```
