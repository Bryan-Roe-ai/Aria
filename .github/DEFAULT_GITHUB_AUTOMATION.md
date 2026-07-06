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

8. **Auto-merge label automation**
    - Workflow: `.github/workflows/auto-merge.yml`
    - Labels `auto-merge` or `autofix` on a PR arm GitHub native auto-merge (squash).
    - When `Merge Gate / All Gates Passed` check succeeds, the `merge-on-gate-pass` job
      validates eligibility and calls the merge API directly.
    - Bot-authored PRs can be automatically approved when `AUTO_MERGE_BOT_APPROVE=true`
      (repository variable) and `AUTO_MERGE_APPROVE_TOKEN` (PAT secret) are configured.
    - Required labels (create manually or via the CLI):
      ```bash
      gh label create auto-merge --color 0075ca --description "Squash-merge when all CI gates pass"
      gh label create autofix    --color e4e669 --description "Auto-merge for automated fix PRs"
      ```
    - Human-authored PRs always require at least one human approval regardless of labels.

9. **Dependabot auto-merge**
    - Workflow: `.github/workflows/dependabot-automerge.yml`
    - Auto-approves and enables squash-merge for Dependabot patch and minor-dev bumps.
    - Major version bumps always require manual review.

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
