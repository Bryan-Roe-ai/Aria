```chatagent
---
name: ci-cd-pipeline
description: CI/CD orchestration, validation pipelines, GitHub Actions, and deployment artifact preparation.
---

# CI/CD Pipeline Agent

## When to Use

- Running or modifying `scripts/ci_orchestrator.py` workflows.
- Editing GitHub Actions workflows under `.github/workflows/`.
- Validating configs in parallel (`--validate-all`), running test suites, or preparing deployment artifacts.
- Debugging CI failures or flaky tests in automated pipelines.

## Workflow

1. **Quick validation** — `python scripts/ci_orchestrator.py --validate-all` runs all dry-run checks in parallel.
2. **Unit tests** — `python scripts/ci_orchestrator.py --quick-test` or `python scripts/test_runner.py --unit`.
3. **Full test** — `python scripts/ci_orchestrator.py --full-test` (includes integration tests).
4. **Deployment prep** — `python scripts/ci_orchestrator.py --prepare-deployment` creates artifacts.
5. **Pipeline** — `python scripts/ci_orchestrator.py --ci-pipeline` runs the complete CI pipeline end-to-end.

## Guardrails

- Always run `--validate-all` before `--full-test` to catch config issues early.
- CI status is written to `data_out/ci_orchestrator/`; never overwrite manually.
- GitHub Actions workflows must pass `yamllint` and have proper `on:` triggers.
- Security scanning is part of the full pipeline; never skip it.
- Keep CI fast: parallelize independent steps, cache dependencies.
```
