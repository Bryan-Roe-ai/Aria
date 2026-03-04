```prompt
---
agent: agent
description: "Implement static content hosting pattern"
---
# Static Content Hosting
## Task
Configure static content hosting with CDN.
## Requirements
1. Serve static assets from CDN/blob storage. 2. Configure cache headers for browser caching.
3. Implement cache busting with content hashing. 4. Enable compression (gzip/brotli).
5. Set up custom domain with TLS.
## Constraints
- Long cache for hashed assets. Short cache for index.html. CDN for global distribution.
## Success Criteria
- Static content cached at edge. Fast global delivery. Cache busting works.
```
