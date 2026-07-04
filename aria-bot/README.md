# Autonomous Dev Bot (Aria Extension)

This module implements an autonomous repository upgrade system designed to continuously improve code quality, maintainability, security, and performance through iterative analysis and safe automated changes.

## Architecture Overview

The system is composed of modular components:

- **Orchestrator**: Controls the upgrade loop and coordinates all modules
- **Analyzer**: Scans repository structure, dependencies, and code quality
- **Planner**: Converts findings into safe upgrade plans
- **Executor**: Applies code changes as minimal diffs
- **Validator**: Runs lint, build, and test checks
- **Risk Manager**: Evaluates safety and prevents destructive changes
- **Commit System**: Handles versioned, atomic commits

## Execution Flow

1. Analyze repository state
2. Generate improvement plan
3. Execute safe changes
4. Validate results
5. Commit changes
6. Repeat cycle

## Design Principles

- Incremental improvements over large rewrites
- Backward compatibility preserved
- Safety-first automation
- Transparent change tracking
- Continuous improvement loop

## Usage

The deterministic loop lives in the `aria_bot` Python package and exposes a
single-cycle CLI:

```bash
# Dry-run (default): analyze + plan, but never touch disk.
python -m aria_bot

# Apply safe fixes to disk (no git commit).
python -m aria_bot --apply

# Apply and create a local git commit (never pushes).
python -m aria_bot --apply --commit
```

Each cycle writes a machine-readable summary to
`data_out/aria_bot/status.json` per the repo's status-file convention.
The status payload now includes both the original top-level totals and a
dashboard-friendly `summary` object with:

- `status_text` — top-level shortcut to the compact cycle status string
- `summary.state` — `dry_run`, `applied`, `no_changes`, or `validation_failed`
- `summary.status_text` — same compact string (also at the top level above)
- `summary.counts` — findings, plans, executions, applied, and skipped counts
- `summary.paths` — applied, skipped, and validated file paths
- `summary.by_kind` — per-kind counts for findings and plans
- `summary.kind_summary` — compact `kind=count` strings for findings and plans

### Sample status.json (dry-run cycle)

```json
{
    "status_text": "dry_run: 2 finding(s), 2 plan(s), 0 applied, 2 skipped",
    "apply": false,
    "commit": false,
    "duration_seconds": 0.041,
    "totals": {
        "findings": 2,
        "plans": 2,
        "executions": 2,
        "applied": 0,
        "skipped": 2
    },
    "applied_paths": [],
    "skipped_paths": ["src/needs_fix.py", "src/needs_newline.md"],
    "summary": {
        "state": "dry_run",
        "status_text": "dry_run: 2 finding(s), 2 plan(s), 0 applied, 2 skipped",
        "counts": {
            "findings": 2,
            "plans": 2,
            "executions": 2,
            "applied": 0,
            "skipped": 2
        },
        "by_kind": {
            "findings": {
                "missing_final_newline": 1,
                "trailing_whitespace": 1
            },
            "plans": { "missing_final_newline": 1, "trailing_whitespace": 1 }
        },
        "kind_summary": {
            "findings": "missing_final_newline=1, trailing_whitespace=1",
            "plans": "missing_final_newline=1, trailing_whitespace=1"
        }
    },
    "validation_ok": null
}
```

The legacy top-level fields remain available for compatibility, including
`totals`, `findings`, `plans`, `executions`, `applied_paths`,
`skipped_paths`, and `validation_targets`.

## Safety Guarantees

These properties are enforced by `aria_bot/risk_manager.py` and cannot be
disabled from configuration:

- **Dry-run by default.** `--apply` is required to write any file.
- **Never pushes.** `commit_system.py` only stages and commits locally.
- **Protected paths** (`datasets/`, `.git/`, `.github/agents/`,
  `data_out/`, `secrets/`, `AI/`, `node_modules/`, `.venv/`, `venv/`,
  `__pycache__/`, `dist/`, `build/`, `.tox/`, `.mypy_cache/`,
  `.ruff_cache/`, `.pytest_cache/`, `htmlcov/`, `coverage/`) are never
  modified.
- **Protected file names** (`.env`, `.env.local`, `local.settings.json`,
  `id_rsa`, `id_ed25519`) are always blocked.
- **Whitelisted transforms only.** v1 supports trailing-whitespace cleanup,
  missing-final-newline fixes, trailing-blank-line trimming, and CRLF→LF
  line-ending normalization — all pure-text and idempotent.
- **No deletions, no renames, no symlink follows.**
- **Per-cycle caps** on plans, file size, and per-plan delta bytes.

Configuration lives in `config/aria_bot.yaml`. Narrowing the operating
envelope (e.g., adding more protected prefixes) is honored; attempts to
widen it past the hard-coded defaults are ignored.

## Adding a New Transform

1. Add a `Finding` kind in `aria_bot/analyzer.py` (with a detector).
2. Add the matching transform function in `aria_bot/executor.py` and
   register it in `_TRANSFORMS`.
3. Add tests under `tests/test_aria_bot.py` covering both detection and
   the idempotency of the transform.

## Future Extensions

- Multi-repo orchestration
- Automated test generation
- Performance benchmarking history
- AI-driven architecture refactoring (would live alongside, not inside,
  this deterministic loop — see `scripts/autonomous_code_agent.py`)
