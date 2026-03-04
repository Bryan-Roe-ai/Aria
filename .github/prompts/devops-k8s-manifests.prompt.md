```prompt
---
agent: agent
description: "Write Kubernetes manifests for application deployment"
---
# Kubernetes Manifests
## Task
Create Kubernetes manifests for application deployment.
## Requirements
1. Deployment with rolling update strategy. 2. Service with appropriate type (ClusterIP, LoadBalancer).
3. ConfigMap and Secret for configuration. 4. Resource requests and limits.
5. Liveness and readiness probes.
## Constraints
- Always set resource limits. Use namespaces. Probes configured. Rolling update.
## Success Criteria
- App deploys and serves traffic. Probes work. Resources bounded. Rolling updates clean.
```
