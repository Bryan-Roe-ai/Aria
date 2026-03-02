#!/usr/bin/env python
"""
Fast validation runner - minimal checks for rapid feedback
Optimized for speed over completeness
"""
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parents[1]


def _find_first_existing(paths: List[str]) -> str | None:
    for rel_path in paths:
        if (REPO_ROOT / rel_path).exists():
            return rel_path
    return None

def quick_check_datasets() -> Dict[str, Any]:
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
        "speed": "instant"
    }

def quick_check_scripts() -> Dict[str, Any]:
    """Verify critical scripts exist without importing."""
    critical = {
        "autotrain": ["scripts/autotrain.py"],
        "test_runner": ["scripts/test_runner.py"],
        "lora_train": [
            "lora/scripts/train_lora.py",
            "AI/microsoft_phi-silica-3.6_v1/scripts/train_lora.py",
        ],
    }
    missing = []
    resolved = {}

    for key, candidates in critical.items():
        found = _find_first_existing(candidates)
        if found is None:
            missing.append(f"{key}: {candidates}")
        else:
            resolved[key] = found
    
    return {
        "status": "ok" if not missing else "missing_scripts",
        "missing": missing,
        "resolved": resolved,
        "speed": "instant"
    }

def quick_check_venv() -> Dict[str, Any]:
    """Check Python venv exists without inspecting packages."""
    venv_markers = [
        ".venv/Scripts/python.exe",
        ".venv/bin/python",
        "venv/Scripts/python.exe",
        "venv/bin/python",
        "quantum/venv/Scripts/python.exe",
        "quantum/venv/bin/python",
        "quantum/.venv/Scripts/python.exe",
        "quantum/.venv/bin/python",
        "lora/.venv/Scripts/python.exe",
        "lora/.venv/bin/python",
        "tools/talk-to-ai/.venv/Scripts/python.exe",
        "tools/talk-to-ai/.venv/bin/python",
    ]
    detected = [m for m in venv_markers if (REPO_ROOT / m).exists()]
    
    return {
        "status": "ok" if detected else "warn_no_venv",
        "venvs_found": len(detected),
        "detected": detected,
        "speed": "instant"
    }

def quick_check_outputs() -> Dict[str, Any]:
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
        "speed": "instant"
    }

def main() -> None:
    """Run all fast checks (completes in <100ms)."""
    parser = argparse.ArgumentParser(description="Fast repository validation")
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Treat warning statuses as failures",
    )
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="Return non-zero exit code when any non-warning check fails",
    )
    args = parser.parse_args()

    print("🚀 Fast Validation (no heavy imports, no parsing)")
    print("=" * 60)
    
    checks = [
        ("Datasets", quick_check_datasets),
        ("Scripts", quick_check_scripts),
        ("Virtual Envs", quick_check_venv),
        ("Output Dirs", quick_check_outputs),
    ]
    
    results: List[Dict[str, Any]] = []
    all_ok = True
    warning_count = 0
    degraded_count = 0
    warning_statuses = {"warn_no_venv"}
    
    for name, func in checks:
        result = func()
        results.append({"check": name, **result})

        if result["status"] == "ok":
            status_icon = "✅"
        elif result["status"] in warning_statuses:
            status_icon = "⚠️"
        else:
            status_icon = "❌"
        print(f"{status_icon} {name:15} - {result['status']}")

        is_warning = result["status"] in warning_statuses
        is_issue = result["status"] != "ok"

        if is_warning:
            warning_count += 1
        elif is_issue:
            degraded_count += 1

        if is_issue:
            all_ok = False
            for key in ["error", "missing", "issues", "detected"]:
                if key in result and result[key]:
                    print(f"   ⚠️  {result[key]}")
    
    print("=" * 60)
    
    # Write results
    output_path = REPO_ROOT / "data_out" / "fast_validate_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "checks": results,
                "all_ok": all_ok,
                "summary": {
                    "warning_count": warning_count,
                    "degraded_count": degraded_count,
                },
            },
            f,
            indent=2,
        )

    should_fail = False
    if args.fail_on_errors and degraded_count > 0:
        should_fail = True
    if args.strict_warnings and warning_count > 0:
        should_fail = True

    if degraded_count > 0 or warning_count > 0:
        print(
            f"⚠️  Partial health: {degraded_count} degraded, {warning_count} warning checks"
        )

    print(f"✅ Validation complete! Results: {output_path.relative_to(REPO_ROOT)}")
    sys.exit(1 if should_fail else 0)

if __name__ == "__main__":
    main()
