```prompt
---
agent: agent
description: "Implement API file upload with multipart form data"
---
# API File Upload
## Task
Implement file upload endpoints with multipart support.
## Requirements
1. Accept `multipart/form-data` with file field.
2. Validate file type, size, and content.
3. Stream large files to avoid memory overload.
4. Generate unique filenames with original extension.
5. Return upload metadata (URL, size, content-type).
## Constraints
- Max file size 100MB. Validate content type (not just extension). Scan for malware if possible.
## Success Criteria
- Files upload and store correctly. Validation enforced. Large files streamed.
```
