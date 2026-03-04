```prompt
---
agent: agent
description: "Implement OAuth 2.0 authorization flows for API"
---
# API OAuth 2.0
## Task
Implement OAuth 2.0 authorization for API access.
## Requirements
1. Support authorization code flow. 2. Support client credentials flow for service-to-service.
3. Implement token endpoint with access/refresh tokens. 4. Support scopes for granular permissions.
5. Validate redirect URIs against whitelist.
## Constraints
- Use PKCE for public clients. TLS required. Short-lived access tokens.
## Success Criteria
- OAuth flows work correctly. Scopes enforced. Tokens validated.
```
