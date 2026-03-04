```prompt
---
agent: agent
description: "Implement federated identity pattern"
---
# Federated Identity
## Task
Implement federated identity for single sign-on.
## Requirements
1. Support multiple identity providers (Azure AD, Google, GitHub). 2. Implement OIDC/SAML federation.
3. Map external identities to internal users. 4. Handle identity linking.
5. Support identity provider switching.
## Constraints
- Validate tokens from each provider. Map claims to internal roles. Handle provider outages.
## Success Criteria
- Multiple identity providers supported. Tokens validated. Roles mapped. SSO works.
```
