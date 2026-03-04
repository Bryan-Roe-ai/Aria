```prompt
---
agent: agent
description: "Run a CI/CD pipeline: validate configs, run tests, and prepare deployment artifacts"
---
# CI Pipeline Run

## Task
Execute a CI/CD pipeline pass: validate all configs, run tests, and report results.

## Context
- CI orchestrator: `scripts/ci_orchestrator.py`
- Test runner: `scripts/test_runner.py`
- Fast validation: `scripts/fast_validate.py`
- GitHub Actions workflows: `.github/workflows/`

## Requirements
1. Run `python scripts/ci_orchestrator.py --validate-all` to check all dry-runs.
2. Execute `python scripts/test_runner.py --unit` for unit tests.
3. Report pass/fail status for each validation step.
4. If all pass, optionally run `--prepare-deployment` for artifacts.
5. Log results to `data_out/ci_orchestrator/`.

## Constraints
- Never skip security scanning in full pipeline runs.
- Keep CI fast: parallelize independent steps.
- CI status files in `data_out/ci_orchestrator/` are machine-readable; don't corrupt them.

## Success Criteria
- All dry-run validations pass.
- All unit tests pass.
- Clear pass/fail report with actionable error messages for failures.
```
