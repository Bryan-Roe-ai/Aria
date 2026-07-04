# Default GitHub Automation (Enabled)

This repository uses a default GitHub automation baseline for quality, safety, and maintenance.

## Included automation

1. **CI + PR quality gate**
    - Workflow: `.github/workflows/merge-gate.yml`
    - Fan-in required check: **`Merge Gate / All Gates Passed`**

2. **Auto-label pull requests by file paths**
    - Workflow: `.github/workflows/labeler.yml`
    - Rules: `.github/labeler.yml`

3. **Stale issue/PR management**
    - Workflow: `.github/workflows/stale.yml`

4. **Dependency update automation**
    - Config: `.github/dependabot.yml`

5. **Dependency security review**
    - Workflow: `.github/workflows/dependency-review.yml`

6. **Baseline verifier (this package)**
    - Workflow: `.github/workflows/default-github-automation.yml`
    - Ensures the baseline files exist and parse correctly.

7. **Ruleset template validator**
    - Workflow: `.github/workflows/ruleset-json-validation.yml`
    - Verifies `.github/rulesets/*.json` structure and required status-check context.

## One-time GitHub settings (manual)

In repository settings, enable branch protection (or rulesets) on `main` with these minimum requirements:

- Require a pull request before merging
- Require approvals before merging
- Require status checks to pass before merging
- Add required check: **`Merge Gate / All Gates Passed`**

> Why manual? Branch protection/ruleset settings are repository settings, not source-controlled workflow logic.

Use these repo files for a fast setup:

- Checklist: `.github/DEFAULT_GITHUB_RULESET_CHECKLIST.md`
- JSON template: `.github/rulesets/main-default-automation.ruleset.json`

## Operational notes

- Keep actions pinned to commit SHAs where practical.
- Keep stale exceptions updated for high-priority labels (`security`, `blocked`, etc.).
- Dependabot PR volume is intentionally capped in `.github/dependabot.yml`.
