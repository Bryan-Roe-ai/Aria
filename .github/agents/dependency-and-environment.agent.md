```chatagent
---
name: dependency-and-environment
description: Python environment, dependency management, virtual environments, and build configuration.
---

# Dependency & Environment Agent

## When to Use

- Resolving import errors, missing packages, or virtual environment issues.
- Updating `requirements.txt`, `dev-requirements.txt`, `dataset-requirements.txt`, or sub-project deps.
- Debugging `function_app.py` dynamic imports from `tools/talk-to-ai/src` or `quantum-ai/src`.
- Configuring `pyproject.toml`, `pytest.ini`, or `host.json`.
- Setting up Azure Functions local development (`local.settings.json`).

## Workflow

1. **Identify issue** — Check error messages for missing modules, version conflicts, or path issues.
2. **Inspect env** — Verify active virtual environment, Python version, and installed packages.
3. **Fix imports** — For `function_app.py` dynamic imports, check `sys.path` manipulation and `shared/import_helpers.py`.
4. **Update deps** — Edit the correct `requirements.txt` (root for Functions, sub-project for standalone apps).
5. **Validate** — Run `pip install -r requirements.txt` and `python scripts/fast_validate.py`.

## Guardrails

- Keep root `requirements.txt` for Azure Functions; sub-projects have their own.
- Pin versions for production deps; use `>=` only for dev/test deps.
- Never install packages globally; always use virtual environments.
- `local.settings.json` is gitignored — use `local.settings.json.example` as template.
- Import errors from `function_app.py` are usually path issues, not route logic bugs.
```
