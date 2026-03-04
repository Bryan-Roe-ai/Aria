```prompt
---
agent: agent
description: "Audit and update Python dependencies across requirements files"
---
# Dependency Audit

## Task
Audit Python dependencies for security vulnerabilities, version staleness, or conflicts.

## Context
- Root: `requirements.txt` (Azure Functions), `dev-requirements.txt`, `dataset-requirements.txt`
- Sub-projects: `cooking-ai/requirements.txt`, `quantum/requirements.txt`, `tools/llm-maker/requirements.txt`, `dashboard/requirements.txt`
- Build config: `pyproject.toml`

## Requirements
1. Identify outdated, vulnerable, or conflicting packages.
2. Update versions with minimal disruption.
3. Keep root `requirements.txt` scoped to Azure Functions runtime.
4. Verify sub-project deps are self-contained.
5. Run `pip install -r requirements.txt` and `python scripts/fast_validate.py` after changes.

## Constraints
- Pin versions for production deps; allow `>=` for dev/test only.
- Never install packages globally; always use virtual environments.
- Check for CVEs in updated packages.
- Don't remove packages without confirming they're unused.

## Success Criteria
- All `requirements.txt` files install cleanly.
- No known CVEs in updated dependencies.
- `python scripts/test_runner.py --unit` passes.
- `python scripts/fast_validate.py` passes.
```
