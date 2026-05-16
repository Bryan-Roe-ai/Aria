# GitHub Ruleset Checklist (Default Automation)

Use this checklist to enforce the repository's default automation on `main`.

## Required check to enforce

- **`Merge Gate / All Gates Passed`**

## Option A: Configure in GitHub UI

Go to **Settings → Rules → Rulesets → New branch ruleset** and configure:

1. **Ruleset name**: `Main Branch - Default Automation Baseline`
2. **Target**: `Branch`
3. **Enforcement status**: `Active`
4. **Branch targeting**: include `main`
5. Enable rules:
   - Restrict deletions
   - Block force pushes
   - Require a pull request before merging
   - Require approvals: `1`
   - Require review from Code Owners
   - Dismiss stale pull request approvals when new commits are pushed
   - Require review thread resolution before merge
   - Require status checks to pass before merging
   - Required status check: **`Merge Gate / All Gates Passed`**

## Option B: Apply JSON via GitHub CLI

This repo includes a ready template:

- `.github/rulesets/main-default-automation.ruleset.json`

Create the ruleset with:

```bash
gh api repos/Bryan-Roe/Aria/rulesets \
  --method POST \
  --input .github/rulesets/main-default-automation.ruleset.json
```

If a ruleset already exists, fetch and update by ID:

```bash
gh api repos/Bryan-Roe/Aria/rulesets
# note the target ruleset id, then:

gh api repos/Bryan-Roe/Aria/rulesets/<RULESET_ID> \
  --method PUT \
  --input .github/rulesets/main-default-automation.ruleset.json
```

## Validation

After applying the ruleset:

- Open a PR to `main`
- Confirm required check appears as **`Merge Gate / All Gates Passed`**
- Confirm merge is blocked until approvals + required checks pass

## Notes

- Rulesets are repository settings, so they are not automatically applied by workflow files.
- Keep this checklist aligned with `.github/workflows/merge-gate.yml` if check names change.
