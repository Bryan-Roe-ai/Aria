```prompt
---
agent: agent
description: "Implement secure DNS configuration and DNSSEC"
---
# Secure DNS
## Task
Configure DNS securely with DNSSEC.
## Requirements
1. Enable DNSSEC validation. 2. Use DNS-over-HTTPS (DoH) for client queries.
3. Implement CAA records for certificate issuance restriction. 4. Monitor for DNS hijacking.
5. Set appropriate TTLs for security-sensitive records.
## Constraints
- CAA records required for all domains. Monitor DNS changes. Low TTL for critical records.
## Success Criteria
- DNSSEC enabled. CAA restricts CAs. DNS changes monitored. DoH configured.
```
