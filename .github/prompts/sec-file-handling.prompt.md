```prompt
---
agent: agent
description: "Implement secure file handling and upload validation"
---
# Secure File Handling
## Task
Implement secure file upload and handling.
## Requirements
1. Validate file type by content (magic bytes), not extension. 2. Limit file size server-side.
3. Store uploads outside webroot. 4. Generate random filenames.
5. Scan uploads for malware.
## Constraints
- Never serve uploaded files directly. Validate both client and server side. No executable uploads.
## Success Criteria
- File types validated by content. Random names used. Stored safely. Malware scanned.
```
