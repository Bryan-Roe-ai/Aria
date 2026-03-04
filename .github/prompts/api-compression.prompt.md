```prompt
---
agent: agent
description: "Implement API response compression with gzip/brotli"
---
# API Compression
## Task
Implement response compression for API efficiency.
## Requirements
1. Support gzip and brotli compression.
2. Parse `Accept-Encoding` header.
3. Set `Content-Encoding` header on compressed responses.
4. Skip compression for small responses (< 1KB).
5. Skip compression for already-compressed content types.
## Constraints
- Compress only text-based responses. Set `Vary: Accept-Encoding`. Don't double-compress.
## Success Criteria
- Large responses compressed. Correct encoding headers set. Small responses skipped.
```
