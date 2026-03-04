```prompt
---
agent: agent
description: "Use pathlib for modern cross-platform file path handling"
---
# Pathlib Migration

## Task
Migrate from os.path to pathlib for modern path handling.

## Requirements
1. Replace `os.path.join()` with `Path() / "subdir"`.
2. Use `Path.resolve()` instead of `os.path.abspath()`.
3. Replace `os.path.exists()` with `Path.exists()`.
4. Use `Path.read_text()` / `Path.write_text()` for file I/O.
5. Use `Path.glob()` / `Path.rglob()` for pattern matching.

## Constraints
- Keep `os.path` for cases where string paths are required by APIs.
- Use `Path(__file__).resolve().parent` for module-relative paths.
- Handle `WindowsPath` vs `PosixPath` transparently.

## Success Criteria
- All path operations use pathlib where possible.
- Cross-platform compatibility maintained.
- Code is more readable and concise.
```
