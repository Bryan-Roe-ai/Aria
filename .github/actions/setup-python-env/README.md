# setup-python-env

Composite GitHub Action to provision Python with pip caching and repository-aware dependency installation.

## Inputs

- `python-version` (default: `3.11`)
- `install-requirements` (default: `true`)
- `requirements-file` (default: `requirements.txt`)
- `install-dev-requirements` (default: `false`)
- `dev-requirements-file` (default: `requirements-dev.txt`)
- `constraints-file` (default: `constraints.txt`)
- `cache-dependency-path` (default: empty)
  - Optional newline-delimited list of dependency files for cache invalidation.
- `extra-requirement-files` (default: empty)
  - Optional newline-delimited list of additional `-r` files to install.
- `extra-packages` (default: empty)
  - Optional space-delimited list of packages to install after requirements files.
- `pip-check-mode` (default: `skip`)
  - `skip`: do not run `python -m pip check`
  - `warn`: run `pip check` but do not fail
  - `enforce`: fail if `pip check` reports dependency issues

## Usage

```yaml
- name: Set up Python for repo tests
  uses: ./.github/actions/setup-python-env
  with:
      python-version: "3.11"
      install-dev-requirements: "true"
      extra-packages: "pytest pytest-cov"
```

```yaml
- name: Set up Python for quantum smoke
  uses: ./.github/actions/setup-python-env
  with:
      install-requirements: "false"
      cache-dependency-path: |
          quantum-ai/requirements-smoke.txt
      extra-requirement-files: |
          quantum-ai/requirements-smoke.txt
      pip-check-mode: "warn"
```
