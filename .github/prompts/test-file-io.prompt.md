```prompt
---
agent: agent
description: "Test file I/O operations for reading, writing, and cleanup"
---
# File I/O Tests
## Task
Write tests for file I/O operations with proper cleanup.
## Requirements
1. Use `tmp_path` fixture for temporary directories.
2. Test reading, writing, appending, and deleting files.
3. Test handling of missing files and permission errors.
4. Test binary vs text mode I/O.
5. Verify cleanup of temporary files after tests.
## Constraints
- Never write to `datasets/` or production paths. Use fixtures for temp dirs.
## Success Criteria
- All file operations tested. Temp files cleaned up. Error cases handled.
```
