#!/usr/bin/env python
"""
Fast validation runner - minimal checks for rapid feedback
Optimized for speed over completeness

Examples:
  python scripts/fast_validate.py
  python scripts/fast_validate.py --json
  python scripts/fast_validate.py --check Dependencies --quiet
  python scripts/fast_validate.py --list-checks
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


_CRITICAL_FAILURES: dict[str, set[str]] = {
    "Datasets": {"missing", "empty"},
    "Scripts": {"missing_scripts"},
    "Output Dirs": {"write_issues"},
    "Configs": {"config_issues"},
    "Dependencies": {"missing_deps"},
}


def is_critical_failure(check_name: str, status: str) -> bool:
    """Return True when a check status should fail fast validation."""
    return status in _CRITICAL_FAILURES.get(check_name, set())


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Build summary metadata for fast-validate checks."""
    total = len(results)
    ok_count = sum(1 for r in results if r.get("status") == "ok")
    critical_failures = [r for r in results if is_critical_failure(str(r.get("check", "")), str(r.get("status", "")))]
    warning_count = total - ok_count - len(critical_failures)

    return {
        "total_checks": total,
        "ok_count": ok_count,
        "warning_count": warning_count,
        "critical_failure_count": len(critical_failures),
        "critical_failure_checks": [r.get("check") for r in critical_failures],
    }


def quick_check_datasets() -> dict[str, Any]:
    """Lightning-fast dataset existence check (no JSONL parsing)."""
    datasets_dir = REPO_ROOT / "datasets"
    if not datasets_dir.exists():
        return {"status": "missing", "error": "datasets/ directory not found"}

    categories = ["chat", "quantum", "vision"]
    found = 0
    for cat in categories:
        cat_dir = datasets_dir / cat
        if cat_dir.exists() and any(cat_dir.iterdir()):
            found += 1

    return {
        "status": "ok" if found > 0 else "empty",
        "categories_found": found,
        "speed": "instant",
    }


def quick_check_scripts() -> dict[str, Any]:
    """Verify critical scripts exist without importing."""
    critical = [
        "autotrain.py",
        "scripts/test_runner.py",
        "ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/train_lora.py",
    ]
    missing = []
    for script in critical:
        if not (REPO_ROOT / script).exists():
            missing.append(script)

    return {
        "status": "ok" if not missing else "missing_scripts",
        "missing": missing,
        "speed": "instant",
    }


def quick_check_venv() -> dict[str, Any]:
    """Check Python virtual environments exist without inspecting packages."""
    venv_markers = [
        ".venv/Scripts/python.exe",
        ".venv/bin/python",
        "venv/Scripts/python.exe",
        "venv/bin/python",
        "ai-projects/quantum-ml/venv/Scripts/python.exe",
        "ai-projects/quantum-ml/venv/bin/python",
        "ai-projects/chat-cli/venv/Scripts/python.exe",
        "ai-projects/chat-cli/venv/bin/python",
    ]
    found = sum(1 for m in venv_markers if (REPO_ROOT / m).exists())

    return {
        "status": "ok" if found > 0 else "no_venv",
        "venvs_found": found,
        "speed": "instant",
    }


def quick_check_outputs() -> dict[str, Any]:
    """Verify output directories writable without listing all files."""
    output_dirs = ["data_out", "deployed_models"]
    issues = []

    for dirname in output_dirs:
        dirpath = REPO_ROOT / dirname
        if not dirpath.exists():
            try:
                dirpath.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"{dirname}: {e}")

    return {
        "status": "ok" if not issues else "write_issues",
        "issues": issues,
        "speed": "instant",
    }


def quick_check_configs() -> dict[str, Any]:
    """Verify critical YAML configs parse without error."""
    import importlib
    import importlib.util

    yaml_mod = importlib.import_module("yaml") if importlib.util.find_spec("yaml") else None

    configs = [
        "config/autonomous_training.yaml",
        "config/master_orchestrator.yaml",
    ]
    issues: list[str] = []
    for cfg in configs:
        path = REPO_ROOT / cfg
        if not path.exists():
            issues.append(f"missing: {cfg}")
            continue
        if yaml_mod:
            try:
                with open(path, encoding="utf-8") as f:
                    yaml_mod.safe_load(f)
            except Exception as exc:
                issues.append(f"parse error in {cfg}: {exc}")

    return {
        "status": "ok" if not issues else "config_issues",
        "issues": issues,
        "speed": "instant",
    }


def quick_check_providers() -> dict[str, Any]:
    """Check which chat providers have required env vars present (no connections)."""
    import os

    providers: dict[str, bool] = {}
    providers["azure_openai"] = all(
        os.environ.get(k)
        for k in [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
        ]
    )
    providers["openai"] = bool(os.environ.get("OPENAI_API_KEY"))
    providers["lmstudio"] = bool(os.environ.get("LMSTUDIO_BASE_URL"))
    providers["cosmos"] = bool(os.environ.get("QAI_ENABLE_COSMOS"))
    providers["sql"] = bool(os.environ.get("QAI_DB_CONN"))

    available = [p for p, v in providers.items() if v]
    return {
        "status": "ok" if available else "no_providers",
        "available": available,
        "speed": "instant",
    }


def quick_check_ai_tokens() -> dict[str, Any]:
    """Check token automation status produced by generate_ai_tokens.py.

    Reads data_out/ai_token_status.json (if present) and reports whether at
    least one provider is healthy. This complements quick_check_providers,
    which only checks env-var presence.
    """
    status_path = REPO_ROOT / "data_out" / "ai_token_status.json"
    if not status_path.exists():
        return {
            "status": "no_token_status",
            "error": "Run `python3 scripts/generate_ai_tokens.py` to create token health status",
            "speed": "instant",
        }

    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "status": "token_status_parse_error",
            "error": f"Invalid JSON in {status_path.name}: {exc}",
            "speed": "instant",
        }

    if not isinstance(payload, dict):
        return {
            "status": "token_status_parse_error",
            "error": (f"Invalid JSON shape in {status_path.name}: expected object"),
            "speed": "instant",
        }

    def _coerce_non_negative_int(value: Any, default: int = 0) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default
        return max(0, parsed)

    healthy = _coerce_non_negative_int(payload.get("healthy", 0))
    total = _coerce_non_negative_int(payload.get("total", 0))
    providers_raw = payload.get("providers", {})
    providers = providers_raw if isinstance(providers_raw, dict) else {}

    # Mark stale if older than 24h to encourage periodic refresh
    last_updated = payload.get("last_updated", "")
    stale = False
    age_seconds: float | None = None
    if isinstance(last_updated, str) and last_updated:
        try:
            # Accept values like 2026-03-29T08:35:15Z and ISO offsets.
            iso_value = last_updated.strip()
            if iso_value.endswith(("Z", "z")):
                iso_value = f"{iso_value[:-1]}+00:00"
            parsed = datetime.fromisoformat(iso_value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            else:
                parsed = parsed.astimezone(timezone.utc)
            age_seconds = max(
                0.0,
                (datetime.now(timezone.utc) - parsed).total_seconds(),
            )
            stale = age_seconds > 24 * 60 * 60
        except ValueError:
            stale = True

    if healthy > 0:
        status = "ok" if not stale else "token_status_stale"
    else:
        status = "no_healthy_token_providers"

    result: dict[str, Any] = {
        "status": status,
        "healthy": healthy,
        "total": total,
        "stale": stale,
        "last_updated": last_updated,
        "providers": providers,
        "speed": "instant",
    }

    if age_seconds is not None:
        result["age_seconds"] = round(age_seconds, 3)
        result["age_hours"] = round(age_seconds / 3600.0, 3)

    return result


def _find_project_python() -> Path | None:
    """Return a likely project Python executable path, preferring local venvs."""
    import os

    if os.name == "nt":
        candidates = [
            REPO_ROOT / ".venv" / "Scripts" / "python.exe",
            REPO_ROOT / "venv" / "Scripts" / "python.exe",
            REPO_ROOT / ".venv" / "bin" / "python",
            REPO_ROOT / "venv" / "bin" / "python",
        ]
    else:
        candidates = [
            REPO_ROOT / ".venv" / "bin" / "python",
            REPO_ROOT / "venv" / "bin" / "python",
            REPO_ROOT / ".venv" / "Scripts" / "python.exe",
            REPO_ROOT / "venv" / "Scripts" / "python.exe",
        ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def _spec_exists_in_python(module_name: str, python_exe: Path) -> bool:
    """Check module availability in a specific interpreter without importing it here."""
    import subprocess

    cmd = [
        str(python_exe),
        "-c",
        ("import importlib.util,sys; sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)"),
        module_name,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    return proc.returncode == 0


def quick_check_dependencies() -> dict[str, Any]:
    """Verify key Python packages are importable (no heavy loads)."""
    import importlib.util

    packages = ["pytest", "yaml", "flask", "azure.functions"]
    present = []
    missing = []
    project_python = _find_project_python()

    for pkg in packages:
        try:
            available_here = bool(importlib.util.find_spec(pkg))
        except ModuleNotFoundError:
            available_here = False

        available_in_project_venv = False
        if not available_here and project_python is not None:
            try:
                available_in_project_venv = _spec_exists_in_python(pkg, project_python)
            except Exception:
                available_in_project_venv = False

        if available_here or available_in_project_venv:
            present.append(pkg)
        else:
            missing.append(pkg)

    details: dict[str, Any] = {
        "status": "ok" if not missing else "missing_deps",
        "present": present,
        "missing": missing,
        "speed": "instant",
    }
    if project_python is not None:
        details["project_python"] = str(project_python.relative_to(REPO_ROOT))

    return details


CHECKS: dict[str, Callable[[], dict[str, Any]]] = {
    "Datasets": quick_check_datasets,
    "Scripts": quick_check_scripts,
    "Virtual Envs": quick_check_venv,
    "Output Dirs": quick_check_outputs,
    "Configs": quick_check_configs,
    "Providers": quick_check_providers,
    "AI Tokens": quick_check_ai_tokens,
    "Dependencies": quick_check_dependencies,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run fast repository validation checks (<100ms, no heavy imports).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/fast_validate.py\n"
            "  python scripts/fast_validate.py --json\n"
            "  python scripts/fast_validate.py --check Dependencies\n"
            "  python scripts/fast_validate.py --list-checks\n"
        ),
    )
    parser.add_argument(
        "--check",
        action="append",
        dest="checks",
        metavar="NAME",
        help="Run only the named check (repeatable). Default: all checks.",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="Print available check names and exit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full result payload as JSON to stdout.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress human-readable table output (use with --json).",
    )
    return parser


def _resolve_checks(selected: Sequence[str] | None) -> list[tuple[str, Callable[[], dict[str, Any]]]]:
    if not selected:
        return list(CHECKS.items())
    missing = [name for name in selected if name not in CHECKS]
    if missing:
        known = ", ".join(CHECKS)
        raise SystemExit(
            f"Unknown check(s): {', '.join(missing)}\n"
            f"Available checks: {known}\n"
            "List checks: python scripts/fast_validate.py --list-checks"
        )
    return [(name, CHECKS[name]) for name in selected]


def run_validation(
    selected: Sequence[str] | None = None,
    *,
    quiet: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any], bool, Path]:
    """Run checks and return results, summary, all_ok, and output path."""
    checks = _resolve_checks(selected)
    results: list[dict[str, Any]] = []
    all_ok = True

    if not quiet:
        print("🚀 Fast Validation (no heavy imports, no parsing)")
        print("=" * 60)

    for name, func in checks:
        result = func()
        row = {"check": name, **result}
        results.append(row)

        critical_failure = is_critical_failure(name, result["status"])
        if critical_failure:
            all_ok = False

        if quiet:
            continue

        if result["status"] == "ok":
            status_icon = "✅"
        elif critical_failure:
            status_icon = "❌"
        else:
            status_icon = "⚠️"
        print(f"{status_icon} {name:15} - {result['status']}")

        if critical_failure:
            for key in ["error", "missing", "issues"]:
                if key in result and result[key]:
                    print(f"   ⚠️  {result[key]}")

    if not quiet:
        print("=" * 60)

    output_path = REPO_ROOT / "data_out" / "fast_validate_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = summarize_results(results)
    payload = {"checks": results, "summary": summary, "all_ok": all_ok}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not quiet:
        print(f"✅ Validation complete! Results: {output_path.relative_to(REPO_ROOT)}")

    return results, payload, all_ok, output_path


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_checks:
        for name in CHECKS:
            print(name)
        return 0

    _, payload, all_ok, output_path = run_validation(
        args.checks,
        quiet=args.quiet or args.json,
    )

    if args.json:
        payload["results_path"] = str(output_path.relative_to(REPO_ROOT))
        print(json.dumps(payload, indent=2))
    elif args.quiet:
        print(f"all_ok={all_ok} results={output_path.relative_to(REPO_ROOT)}")

    print(f"✅ Validation complete! Results: {output_path.relative_to(REPO_ROOT)}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    raise SystemExit(main())
