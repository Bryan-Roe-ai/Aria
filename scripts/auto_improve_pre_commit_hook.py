#!/usr/bin/env python3
"""Pre-commit hook for auto-improve checks.

This hook is configured in .pre-commit-config.yaml as a local hook.
It runs a lightweight auto-improve validation before allowing commits.

Usage:
  pre-commit run auto-improve --all-files
  pre-commit install  # Install hook for automatic execution
  pre-commit uninstall  # Remove hook

Exit codes:
  0: All checks passed
  1: Issues found (with auto-fix option if --fix passed)
  2: Configuration error
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_ruff_check(fix: bool = False) -> bool:
    """Run ruff checks on staged Python files.

    Args:
        fix: If True, apply ruff fixes automatically

    Returns:
        True if check passed or fixes applied, False if issues remain
    """
    cmd = ["ruff", "check"]
    if fix:
        cmd.append("--fix")
    cmd.append(".")

    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return False

    return True


def run_format_check(fix: bool = False) -> bool:
    """Run ruff format checks.

    Args:
        fix: If True, apply formatting fixes automatically

    Returns:
        True if check passed or fixes applied, False if issues remain
    """
    cmd = ["ruff", "format"]
    if not fix:
        cmd.append("--check")
    cmd.append(".")

    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return False

    return True


def run_health_check() -> bool:
    """Run lightweight repo health validation.

    Returns:
        True if health check passed, False if issues found
    """
    # Run a quick health check (without full pytest or endpoints)
    cmd = [
        sys.executable,
        "scripts/repo_health_automation.py",
        "--once",
        "--continue-on-fail",
    ]

    subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    # Parse status.json to determine success
    status_file = (
        REPO_ROOT / "data_out" / "repo_health_automation" / "status.json"
    )
    if status_file.exists():
        try:
            with open(status_file, encoding="utf-8") as f:
                status = json.load(f)
                if not status.get("succeeded", False):
                    print(f"Health check failed: {status}", file=sys.stderr)
                    return False
        except (json.JSONDecodeError, KeyError) as e:
            print(
                f"Warning: Could not parse health check status: {e}",
                file=sys.stderr,
            )
            # Don't fail on status parsing errors
            return True

    return True


def main() -> int:
    """Main entry point for pre-commit hook.

    Returns:
        0 if all checks passed
        1 if issues found
        2 if configuration error
    """
    parser = argparse.ArgumentParser(
        description="Pre-commit hook for auto-improve checks"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues with ruff",
    )
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip full health check (just run ruff)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (unused; hook checks all files)",
    )

    args = parser.parse_args()

    print("🔍 Running auto-improve pre-commit checks...")

    checks_passed = True

    # 1. Ruff check
    print("  • Checking code with ruff...", end="", flush=True)
    if not run_ruff_check(fix=args.fix):
        print(" ❌")
        checks_passed = False
    else:
        print(" ✅")

    # 2. Format check
    print("  • Checking code formatting...", end="", flush=True)
    if not run_format_check(fix=args.fix):
        print(" ❌")
        checks_passed = False
    else:
        print(" ✅")

    # 3. Health check (optional, can be slow)
    if not args.skip_health_check:
        print("  • Running health checks...", end="", flush=True)
        if not run_health_check():
            print(" ⚠️  (non-blocking)")
            # Don't fail on health check issues
        else:
            print(" ✅")

    if checks_passed:
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Fix issues before committing")
        if not args.fix:
            print("💡 Tip: Run with --fix to auto-correct issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
