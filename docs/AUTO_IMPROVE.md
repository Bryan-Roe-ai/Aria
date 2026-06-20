# Auto-Improve Repository Workflow

Automated code quality and repository health maintenance for the Aria platform.

## Overview

The auto-improve workflow provides:

- **Automatic linting fixes** (ruff) for Python code
- **Repository health checks** (validation, configuration audits, endpoint smoke tests)
- **Graceful failure handling** (continues on transient issues, doesn't block the repo)
- **Status tracking** (results logged to `data_out/repo_health/status.json`)

The workflow is designed for:

- One-shot runs during development or CI/CD
- Continuous daemon mode (background monitoring/fixing)
- Integration with existing orchestrators and automation

## Quick Start

### One-shot auto-improve

Run a single improvement cycle with ruff fixes and strict endpoint validation:

```bash
python run_automation.py --auto-improve --strict-endpoints
```

**Flags:**

- `--auto-improve`: Enable auto-improve mode
- `--strict-endpoints`: Use strict HTTP endpoint validation (requires running server)
- `--full-pytest`: Include full pytest smoke tests during improvement cycle

### Continuous auto-improve daemon

Start a background daemon that runs auto-improve every 60 minutes:

```bash
# Default: auto-improve enabled, strict endpoints
python run_continuous_automation.py --interval 60 --strict-endpoints

# Disable auto-improve in continuous mode
python run_continuous_automation.py --interval 60 --no-auto-improve

# Include full pytest in each cycle
python run_continuous_automation.py --interval 60 --strict-endpoints --full-pytest
```

### VS Code Tasks

Use built-in VS Code tasks for quick access:

- **`automation: auto-improve-repo-once`** — Run once with strict endpoints
- **`automation: auto-improve-repo-watch`** — Start continuous daemon (logs to `logs/continuous_automation.log`)

## What Gets Fixed

### Automatic Fixes (Ruff)

The workflow runs `ruff check --fix` on Python files to auto-fix common issues:

- Import sorting
- Unused imports
- Line length violations
- Type annotation modernization
- Exception handling patterns

### Repository Health Checks

The workflow validates:

- **Environment setup** (Python version, venv, core dependencies)
- **Project structure** (required directories and files)
- **Configuration** (YAML parsing, schema validation)
- **Database connectivity** (SQL pool saturation, Cosmos availability)
- **Provider detection chain** (LM Studio, Ollama, Azure OpenAI, OpenAI, local fallback)
- **Endpoint smoke tests** (HTTP routes respond correctly)

### Status Output

Results are written to `data_out/repo_health/status.json`:

```json
{
  "updated_at": "2026-06-20T12:34:56Z",
  "total_cycles": 5,
  "successful_cycles": 4,
  "failed_cycles": 1,
  "last_cycle": {
    "started_at": "2026-06-20T12:30:00Z",
    "completed_at": "2026-06-20T12:34:56Z",
    "succeeded": true,
    "steps": [
      {
        "name": "ruff_check_fix",
        "command": ["ruff", "check", "--fix", "."],
        "exit_code": 0,
        "duration_seconds": 15
      }
    ]
  }
}
```

## Safety & Resilience

### Graceful Degradation

The workflow continues on transient failures:

- Local services not running (Ollama, LM Studio) → warning, continues
- Filesystem permission errors → warning, continues
- Optional dependencies missing → warning, continues
- Endpoint tests fail → warning, continues

### No Breaking Changes

- Only applies safe, reversible fixes (linting, formatting)
- Never deletes files or data in `datasets/`
- Never modifies production configs without explicit flag
- Status file writes are defensive (fails gracefully if permissions denied)

### Dry-Run Support

Orchestrators wrapped by auto-improve support `--dry-run`:

```bash
python scripts/repo_health_automation.py --once --dry-run --auto-fix-ruff
```

## Configuration

Auto-improve behavior is controlled via CLI flags. No config file is required.

**Common patterns:**

```bash
# Development: fast cycle with fixes
python run_automation.py --auto-improve

# CI/CD: strict validation, full tests
python run_automation.py --auto-improve --strict-endpoints --full-pytest

# Background daemon: relaxed continuous improvement
python run_continuous_automation.py --interval 120 --no-auto-improve

# Aggressive continuous: strict + full pytest every 30 minutes
python run_continuous_automation.py --interval 30 --strict-endpoints --full-pytest
```

## Integration with Other Workflows

Auto-improve integrates with existing orchestrators:

- **Autonomous Training**: Auto-improve can run before/after training cycles
- **Quantum ML**: Validates quantum pipeline configuration and provider availability
- **Chat CLI**: Checks provider detection chain and memory system health
- **Aria Character**: Validates web server routes and action schema

Example: Run training, then auto-improve:

```bash
python scripts/autotrain.py --quick && python run_automation.py --auto-improve
```

## Monitoring

### Live Status

Check auto-improve status in real-time:

```bash
cat data_out/repo_health/status.json | python -m json.tool
```

### Logs

Continuous daemon logs are written to:

- `logs/continuous_automation.log` (main daemon output)
- `data_out/repo_health/*.log` (individual cycle logs)

View live logs:

```bash
tail -f logs/continuous_automation.log
```

## Troubleshooting

### Workflow exits immediately

- Check Python version: `python --version` (requires 3.9+)
- Verify venv is activated: `.venv/bin/python --version`
- Check workspace path: `pwd` (should be repo root)

### Ruff fixes fail

- Ensure ruff is installed: `.venv/bin/pip list | grep ruff`
- Reinstall: `.venv/bin/pip install ruff`

### Endpoint tests fail

- Start Azure Functions: `func host start --port 7071`
- Start Aria server: `python apps/aria/server.py --port 8080`
- Or disable strict mode: `python run_automation.py --auto-improve` (without `--strict-endpoints`)

### Status file not writable

- Check `data_out/` permissions: `ls -la data_out/`
- Create if missing: `mkdir -p data_out/repo_health`
- Workflow continues gracefully if status write fails

## Next Steps

- **Run once**: `python run_automation.py --auto-improve --strict-endpoints`
- **Run continuous**: `python run_continuous_automation.py --interval 60 --strict-endpoints`
- **Monitor**: `tail -f logs/continuous_automation.log`
- **Review**: `cat data_out/repo_health/status.json | python -m json.tool`

For more details, see `.github/copilot-instructions.md` and `AGENTS.md`.
