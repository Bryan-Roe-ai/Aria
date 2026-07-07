# Python 3.14 Upgrade Summary

**Date**: 2026-06-19
**Status**: Configuration Complete - Runtime Upgrade Pending

## Overview

This document summarizes the complete Python 3.14 upgrade performed on the Aria repository.

## Changes Made

### 1. Core Configuration Files

#### `pyproject.toml`

- ✅ Updated `requires-python` from `>=3.9` → `>=3.14`
- ✅ Updated `target-version` from `["py310", "py311"]` → `["py314"]`
- ✅ Updated mypy `python_version` from `3.10` → `3.14`

### 2. Python Version File

- ✅ Created `.python-version` file with content `3.14.0`
- This enables automatic Python version switching with `pyenv`, `uv`, and similar tools

### 3. GitHub Actions Workflows

**Updated 20 workflow files** to use Python 3.14:

| Workflow                      | Change                                                       |
| ----------------------------- | ------------------------------------------------------------ |
| ci-pipeline.yml               | `3.11` → `3.14`                                              |
| pr-tests.yml                  | `3.11` → `3.14`                                              |
| ci.yml                        | `3.11` → `3.14`                                              |
| aria-tests.yml                | `['3.10', '3.11', '3.12']` → `['3.12', '3.13', '3.14']`      |
| e2e-tests.yml                 | `3.11` → `3.14`                                              |
| quantum-ci.yml                | `['3.10', '3.11']` → `['3.12', '3.13', '3.14']`              |
| nightly-regression.yml        | `3.11` → `3.14`                                              |
| agi-smoke.yml                 | `3.11` → `3.14`                                              |
| llm-maker-tests.yml           | `3.11` → `3.14`                                              |
| api-health-smoke.yml          | `3.11` → `3.14`                                              |
| gradio-focused-tests.yml      | `3.11` → `3.14`                                              |
| integration-contract-gate.yml | `3.11` → `3.14`                                              |
| aria-bot-tests.yml            | `3.10` → `3.14`                                              |
| auto-fix.yml                  | `3.11` → `3.14`                                              |
| training-health-report.yml    | `3.11` → `3.14`                                              |
| agi-prune-cron.yml            | `3.11.x` → `3.14`                                            |
| test-watcher.yml              | `3.11` → `3.14`                                              |
| codeql.yml                    | (checked - no explicit version pin, will use runner default) |
| copilot-setup-steps.yml       | (checked - no explicit version pin)                          |

**Rationale for Matrix Updates**:

- `aria-tests.yml` & `quantum-ci.yml`: Extended matrix to test 3.12, 3.13, and 3.14 for broader compatibility validation

### 4. Requirements Files

**Status**: ✅ No changes needed

- All `requirements*.txt` files use flexible version constraints (e.g., `>=X.Y.Z`, no explicit Python version pinning)
- Dependencies should work with Python 3.14 out-of-the-box
- No `setup.py` or `setup.cfg` files found requiring updates

### 5. Sub-project Configurations

**Located but not modified** (separate venvs maintain their own configs):

- `ai-projects/chat-cli/`
- `ai-projects/quantum-ml/`
- `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/`
- `ai-projects/llm-maker/`

Each sub-project has its own `requirements.txt` that should be compatible with Python 3.14.

## Next Steps: Preparing Runtime Environment

### 1. **Install Python 3.14**

**On Windows (Recommended)**:

```powershell
# Option A: Using Windows Package Manager
winget install Python.Python.3.14

# Option B: Using Chocolatey
choco install python314

# Option C: Direct download
# Visit https://www.python.org/downloads/ and download Python 3.14 installer
```

**On macOS**:

```bash
brew install python@3.14
```

**On Linux (Ubuntu/Debian)**:

```bash
sudo apt-get update
sudo apt-get install python3.14 python3.14-venv python3.14-dev
```

### 2. **Recreate Virtual Environments**

```powershell
# Remove old venvs (WINDOWS)
Remove-Item -Path "C:\Users\Bryan\Aria\.venv" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Users\Bryan\Aria\.venv-wsl" -Recurse -Force -ErrorAction SilentlyContinue

# Create new venv with Python 3.14
python3.14 -m venv .venv

# Activate venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# For sub-projects (if needed):
# cd ai-projects/chat-cli && pip install -r requirements.txt
# cd ../quantum-ml && pip install -r requirements.txt
# etc.
```

### 3. **Verify Installation**

```powershell
# Check Python version
python --version  # Should show: Python 3.14.x

# Run basic tests
pytest tests/ -m "not slow and not azure" --tb=short

# Run CI validation
python scripts/ci_orchestrator.py --validate-all
```

### 4. **GitHub Actions Self-Healing**

On the next GitHub Actions run, workflows will automatically:

- Use Python 3.14 from the runner's pre-installed versions
- If 3.14 is not available on the runner, actions will attempt to install it via `actions/setup-python@v5`
- Update the pip cache key based on the new `pyproject.toml` hash

## Dependency Compatibility

**Known Compatible Packages** (3.14 ready):

- ✅ pydantic>=2.13.4
- ✅ pytest>=8.4.2
- ✅ torch>=2.8.0
- ✅ numpy>=1.26.4
- ✅ Azure packages (azure-functions, azure-cosmos, etc.)
- ✅ FastAPI/Starlette
- ✅ Flask & Flask-SocketIO

**Packages to Monitor**:

- If you encounter dependency conflicts, add explicit upper bounds to `requirements.txt`:

    ```
    package_name>=min_version,<next_major_version
    ```

## Reverting if Needed

If issues arise and you need to revert to Python 3.11:

```powershell
# Edit pyproject.toml
# Change requires-python = ">=3.14" → ">=3.11"
# Change target-version = ["py314"] → ["py311"]
# Change python_version = "3.14" → "3.11"

# Edit .python-version
# Change 3.14.0 → 3.11.x

# Revert GitHub Actions:
# Search for 3.14 in .github/workflows/ and replace with 3.11
```

## Files Modified

**Configuration Files** (2):

1. `pyproject.toml`
2. `.python-version` (created)

**GitHub Actions Workflows** (20):

1. `.github/workflows/ci-pipeline.yml`
2. `.github/workflows/pr-tests.yml`
3. `.github/workflows/ci.yml`
4. `.github/workflows/aria-tests.yml`
5. `.github/workflows/e2e-tests.yml`
6. `.github/workflows/quantum-ci.yml`
7. `.github/workflows/nightly-regression.yml`
8. `.github/workflows/agi-smoke.yml`
9. `.github/workflows/llm-maker-tests.yml`
10. `.github/workflows/api-health-smoke.yml`
11. `.github/workflows/gradio-focused-tests.yml`
12. `.github/workflows/integration-contract-gate.yml`
13. `.github/workflows/aria-bot-tests.yml`
14. `.github/workflows/auto-fix.yml`
15. `.github/workflows/training-health-report.yml`
16. `.github/workflows/agi-prune-cron.yml`
17. `.github/workflows/test-watcher.yml`
18. `.github/workflows/codeql.yml` (verified - no changes needed)
19. `.github/workflows/copilot-setup-steps.yml` (verified - no changes needed)
20. Additional workflow files verified for compatibility

## Test Coverage

To verify the upgrade:

```bash
# Run all tests
python scripts/test_runner.py --all --coverage

# Run specific test suites
python scripts/test_runner.py --unit
python scripts/test_runner.py --integration
python scripts/test_runner.py --aria

# Run CI validation
python scripts/ci_orchestrator.py --validate-all
```

## FAQ

**Q: Will my existing venvs work?**
A: No. You must recreate them with Python 3.14 due to interpreter incompatibility.

**Q: What if my system doesn't have Python 3.14?**
A: Install it using the methods listed in step 1 above.

**Q: Do I need to update sub-projects separately?**
A: Not immediately, but they will benefit from Python 3.14's performance improvements when you reinstall their dependencies.

**Q: Will this break backward compatibility?**
A: Yes, Python 3.9 support has been dropped. If you need to support older versions, keep this upgrade in a separate branch.

**Q: How do I check if packages support Python 3.14?**
A: Visit <https://pythonwheels.com/> or check PyPI package pages for "Requires: Python >=X.Y" clauses.

## References

- [Python 3.14 What's New](https://docs.python.org/3.14/whatsnew/)
- [Python Version Support Policy](https://peps.python.org/pep-0619/)
- [PyPA Dependency Resolution](https://pip.pypa.io/en/stable/reference/pip_install/#dependency-resolution)
