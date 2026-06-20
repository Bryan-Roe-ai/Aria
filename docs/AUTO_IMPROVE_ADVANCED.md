# Auto-Improve CI/CD, Pre-Commit, Alerts & Custom Rules

Complete guide to integrating auto-improve with GitHub Actions, pre-commit hooks,
health check alerts, and custom validation rules.

## Overview

The auto-improve system now includes four integrated components:

1. **GitHub Actions CI/CD** — Automated health checks in pull request pipelines
2. **Pre-Commit Hooks** — Local developer validation before commits
3. **Health Check Alerts** — Notifications when issues are detected
4. **Custom Validation Rules** — Extensible framework for domain-specific rules

## 1. GitHub Actions CI/CD Integration

### Workflow: `auto-improve-ci.yml`

Automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Daily at 3 AM UTC
- Manual trigger via GitHub UI

### Jobs

#### `auto-improve-check`
- Runs full health check cycle
- Comments PR with results
- Uploads artifacts for inspection
- Non-blocking (doesn't prevent merge)

#### `auto-improve-enforcement`
- Runs ruff checks on pull requests
- Blocks merge if formatting/linting fails
- Posts code quality summary comment

### Usage

View workflow status:
```bash
# In GitHub Actions UI
https://github.com/Bryan-Roe/Aria/actions/workflows/auto-improve-ci.yml

# Or trigger manually via gh CLI
gh workflow run auto-improve-ci.yml --ref main
```

### Configuration

Customize in `.github/workflows/auto-improve-ci.yml`:

```yaml
# Change schedule
schedule:
  - cron: "0 3 * * *"  # Daily at 3 AM UTC

# Add notification webhook
env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 2. Pre-Commit Hooks Integration

### Setup

Install pre-commit framework:
```bash
pip install pre-commit
pre-commit install
```

Verify installation:
```bash
pre-commit run --all-files
```

### Hook: `auto-improve-checks`

Runs automatically before every commit. Checks:
- Ruff linting
- Code formatting
- Quick health validation

### Usage

**Auto-fix issues before commit:**
```bash
# Manually run hook with --fix
python scripts/auto_improve_pre_commit_hook.py --fix

# Or use pre-commit framework
pre-commit run auto-improve-checks --all-files --verbose

# Skip health check if too slow (dev-only)
python scripts/auto_improve_pre_commit_hook.py --fix --skip-health-check
```

**Bypass hook temporarily** (not recommended):
```bash
git commit --no-verify
```

**Update hook configuration:**
```yaml
# In .pre-commit-config.yaml
- id: auto-improve-checks
  # Customize stages where hook runs
  stages: [commit, push, manual]

  # Or skip by default, run manually
  stages: [manual]
```

Then run manually with:
```bash
pre-commit run auto-improve-checks --all-files
```

## 3. Health Check Alerts System

### Alert Types

#### Failure Alerts
Triggered when health check cycle fails:
- Failed ruff checks
- Environment setup issues
- Provider detection failures
- Database connectivity errors

#### Degradation Alerts
Triggered for performance issues:
- Health check cycle took > 60 seconds
- Repeated failures in consecutive cycles
- Memory/CPU spikes

#### Recovery Alerts
Triggered when issues are resolved:
- All checks passing after previous failures
- Performance back to normal

### Configuration

Set environment variables for notifications:

```bash
# Email alerts
export ALERT_EMAIL="dev-team@example.com"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="noreply@example.com"
export SMTP_PASS="app-password"

# Slack alerts
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../X..."

# GitHub alerts (automatic in CI)
# No configuration needed if running in GitHub Actions
```

### Usage

**Check now and send alerts:**
```bash
python scripts/health_check_alerts.py --check-now
```

**Watch continuously (daemon mode):**
```bash
python scripts/health_check_alerts.py --watch --interval 300
# Check every 5 minutes and alert on issues
```

**Disable notifications (check only):**
```bash
python scripts/health_check_alerts.py --check-now --no-alerts
```

**View alert history:**
```bash
cat data_out/health_check_alerts.json | python -m json.tool
```

### Integration with Automation

Add to continuous automation:

```bash
# In run_continuous_automation.py, auto-improve runs every interval
python run_continuous_automation.py --interval 300 --strict-endpoints

# Add alert watcher in separate window
python scripts/health_check_alerts.py --watch --interval 300
```

Or run together in background:
```bash
# Terminal 1: Auto-improve cycles
python run_continuous_automation.py --interval 300 --strict-endpoints &

# Terminal 2: Alert watcher
python scripts/health_check_alerts.py --watch --interval 300 &

# Monitor: tail -f logs/continuous_automation.log
```

## 4. Custom Validation Rules Framework

### Create a Custom Rule

Create a new rule file (example: `scripts/rules/my_custom_rule.py`):

```python
from scripts.custom_validation_rules import (
    ValidationRule,
    ValidationIssue,
    registry,
)

class MyCustomRule(ValidationRule):
    """Check that all CLI scripts have repo root in sys.path."""

    name = "cli-sys-path-check"
    category = "code"  # code, config, security, performance, custom
    description = "Verify CLI scripts import repo root"
    severity = "medium"

    def validate(self):
        issues = []
        for script in Path("scripts").glob("*.py"):
            with open(script) as f:
                content = f.read()
                if "sys.path.insert" not in content:
                    issues.append(
                        ValidationIssue(
                            severity="high",
                            message="Missing sys.path setup",
                            file=str(script.relative_to(Path.cwd())),
                            remediation="Add sys.path.insert(0, str(REPO_ROOT))"
                        )
                    )
        return issues

# Register the rule
registry.register(MyCustomRule())
```

### Rule Categories

- **code** — Code quality, style, documentation
- **config** — Configuration files, YAML/JSON validation
- **security** — Secrets, permissions, unsafe patterns
- **performance** — Slow operations, resource issues
- **custom** — Domain-specific rules

### Built-in Rules

#### `no-hardcoded-secrets` (security)
Scans for hardcoded API keys, tokens, passwords.

```bash
python scripts/custom_validation_rules.py --run --rules no-hardcoded-secrets
```

#### `requirements-consistency` (config)
Validates requirements.txt and constraints.txt don't have conflicts.

#### `docstring-coverage` (code)
Checks that functions have docstrings.

#### `config-validation` (config)
Validates YAML configuration files for syntax errors.

### Usage

**List all rules:**
```bash
python scripts/custom_validation_rules.py --list
```

**Run all rules:**
```bash
python scripts/custom_validation_rules.py --run
```

**Run specific rules:**
```bash
python scripts/custom_validation_rules.py --run --rules no-hardcoded-secrets,config-validation
```

**Output as JSON:**
```bash
python scripts/custom_validation_rules.py --run --json > validation-report.json
```

### Integration with Health Check

The custom rules are automatically included in health check cycles:

```bash
# Runs custom validation rules as part of health check
python run_automation.py --auto-improve --strict-endpoints
```

Status file includes rule results:
```bash
cat data_out/repo_health_automation/status.json | jq '.custom_validations'
```

## Complete Workflows

### Workflow 1: Local Development Cycle

```bash
# 1. Work on code
git add .

# 2. Pre-commit hook runs automatically
# (ruff fixes, format check, health validation)

# 3. If hook fails, review and fix
python scripts/auto_improve_pre_commit_hook.py --fix

# 4. Commit
git commit -m "feat: add feature"

# 5. Push
git push origin feature-branch
```

### Workflow 2: CI/CD Pipeline

```
1. PR created
   ↓
2. GitHub Actions: auto-improve-ci.yml triggers
   - Runs health checks (non-blocking)
   - Runs ruff enforcement (blocking)
   - Comments PR with results
   ↓
3. If enforcement job fails:
   - Merge blocked
   - Developer runs locally: python run_automation.py --auto-improve --fix
   - Re-pushes
   ↓
4. If health checks fail:
   - Alert system notifies (Slack, email, GitHub)
   - Team reviews and investigates
   ↓
5. Merge once all checks pass
```

### Workflow 3: Continuous Monitoring

```bash
# In background (or separate terminal)
python run_continuous_automation.py --interval 300 --strict-endpoints &
python scripts/health_check_alerts.py --watch --interval 300 &

# Monitor
tail -f logs/continuous_automation.log
tail -f data_out/health_check_alerts.json | python -m json.tool
```

### Workflow 4: Custom Rule Enforcement

Add custom rules to your CI/CD:

```yaml
# In .github/workflows/auto-improve-ci.yml
- name: Run custom validation rules
  run: |
    python scripts/custom_validation_rules.py --run --json > validations.json
    if grep -q '"severity": "critical"' validations.json; then
      echo "❌ Critical validation failures"
      exit 1
    fi
```

## Troubleshooting

### Pre-Commit Hook Failing

**Problem:** Hook rejects commit

**Solution:**
```bash
# See what's failing
python scripts/auto_improve_pre_commit_hook.py --no-fix

# Auto-fix issues
python scripts/auto_improve_pre_commit_hook.py --fix

# Skip health check if slow
python scripts/auto_improve_pre_commit_hook.py --fix --skip-health-check
```

### Alerts Not Sending

**Problem:** No emails/Slack messages

**Check configuration:**
```bash
# Email
echo $SMTP_HOST $SMTP_PORT $ALERT_EMAIL

# Slack
echo $SLACK_WEBHOOK_URL

# Test alert
python scripts/health_check_alerts.py --check-now
```

### Custom Rule Not Running

**Problem:** Rule doesn't execute

**Check registration:**
```bash
python scripts/custom_validation_rules.py --list
# Should show your rule

# Run with verbose output
python scripts/custom_validation_rules.py --run --rules your-rule-name
```

## Best Practices

1. **Pre-Commit Local Development**
   - Let pre-commit hooks run — they catch issues early
   - Use `--fix` flag to auto-correct most issues
   - Skip only if you understand the cost

2. **CI/CD Health Checks**
   - Monitor GitHub Actions workflow runs
   - Investigate failures promptly
   - Track performance trends

3. **Alert Configuration**
   - Set up email or Slack for team visibility
   - Review alerts regularly (not spam)
   - Adjust thresholds for your use case

4. **Custom Rules**
   - Keep rules simple and focused
   - Write rules for your team's conventions
   - Test rules before committing
   - Document rule's purpose and remediation

5. **Maintenance**
   - Review and update custom rules quarterly
   - Remove rules that always pass
   - Refine based on team feedback

## Next Steps

1. ✅ GitHub Actions workflow is active
2. Install pre-commit locally: `pre-commit install`
3. Configure alerts: Set `SLACK_WEBHOOK_URL` or `ALERT_EMAIL`
4. Create first custom rule for your team's convention
5. Integrate into CI/CD pipeline

## Files

- `.github/workflows/auto-improve-ci.yml` — GitHub Actions workflow
- `scripts/auto_improve_pre_commit_hook.py` — Pre-commit hook implementation
- `scripts/health_check_alerts.py` — Alert system
- `scripts/custom_validation_rules.py` — Validation framework
- `.pre-commit-config.yaml` — Pre-commit configuration

See also:
- [AUTO_IMPROVE.md](./AUTO_IMPROVE.md) — Basic auto-improve usage
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) — Quick commands
