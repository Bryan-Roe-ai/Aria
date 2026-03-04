```prompt
---
agent: agent
description: "Create or modify a GitHub Actions workflow YAML file"
---
# GitHub Actions Workflow

## Task
Create or update a GitHub Actions CI/CD workflow.

## Context
- Workflows: `.github/workflows/` (ci-pipeline, code-quality, codeql, e2e-tests, release, etc.)
- Workflow docs: `.github/WORKFLOWS.md`, `.github/workflows/README.md`
- CI orchestrator: `scripts/ci_orchestrator.py`
- Existing patterns: `aria-tests.yml`, `pr-checks.yml`, `auto-validation.yml`

## Requirements
1. Define clear `name:` and `on:` triggers (push, pull_request, schedule, workflow_dispatch).
2. Pin action versions to full SHA or major version tag.
3. Use GitHub Secrets for credentials; never hardcode.
4. Cache dependencies with `actions/cache` for speed.
5. Use `concurrency:` to prevent duplicate runs.
6. Add status badge to `README.md` if appropriate.

## Constraints
- Workflow YAML must pass `yamllint`.
- One workflow per concern (CI, deploy, release, quality scan).
- Keep total CI time reasonable; parallelize independent jobs.
- Update `.github/WORKFLOWS.md` when adding new workflows.

## Success Criteria
- Workflow triggers correctly on the specified events.
- All jobs pass on a clean run.
- Secrets are used securely; no hardcoded tokens.
- WORKFLOWS.md updated with the new workflow entry.
```
