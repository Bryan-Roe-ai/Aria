```prompt
---
agent: agent
description: "Resolve Python import errors, path issues, or virtual environment problems"
---
# Environment Fix

## Task
Resolve import errors, missing packages, or environment configuration issues.

## Context
- Entry point: `function_app.py` — dynamically imports from `tools/talk-to-ai/src` and `quantum-ai/src`
- Import helpers: `shared/import_helpers.py`
- Requirements: `requirements.txt` (root), plus sub-project `requirements.txt` files
- Local settings: `local.settings.json` (gitignored), template at `local.settings.json.example`
- Build config: `pyproject.toml`, `pytest.ini`

## Requirements
1. Reproduce the import error or environment failure.
2. Check `sys.path` manipulation in the failing module and `shared/import_helpers.py`.
3. Verify the package is in the correct `requirements.txt`.
4. Install missing deps and validate.
5. If path-related, fix the import helper or add the correct `sys.path.insert`.

## Constraints
- Don't modify `local.settings.json` directly (it's gitignored); update the example file.
- Import errors from `function_app.py` are usually path issues, not route logic bugs.
- Always use virtual environments; never install globally.
- Keep sub-project deps self-contained.

## Success Criteria
- Import succeeds without errors.
- `python scripts/fast_validate.py` passes.
- `python scripts/test_runner.py --unit` passes.
```
