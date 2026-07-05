from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate drift between MCP suite artifacts (normal vs strict)."
        )
    )
    parser.add_argument(
        "--base",
        default="data_out/mcp_validation_suite.json",
        help="Path to non-strict suite artifact JSON.",
    )
    parser.add_argument(
        "--strict",
        default="data_out/mcp_validation_suite_strict.json",
        help="Path to strict suite artifact JSON.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return summary if isinstance(summary, dict) else {}


def compare(
    base: dict[str, Any],
    strict: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    base_s = get_summary(base)
    strict_s = get_summary(strict)

    if base_s.get("env_strict") is True:
        warnings.append(
            "Base artifact has env_strict=true "
            "(expected false or absent)."
        )

    if strict_s.get("env_strict") is not True:
        errors.append("Strict artifact missing env_strict=true in summary.")

    # These fields should not drift unexpectedly between
    # strict and non-strict runs.
    for key in ("config_ok", "runtime_ok", "all_ok"):
        if base_s.get(key) != strict_s.get(key):
            errors.append(
                "Summary drift detected for "
                f"'{key}': base={base_s.get(key)} "
                f"strict={strict_s.get(key)}"
            )

    # sanity check: strict should remain explicitly strict
    if (
        strict_s.get("all_ok") is True
        and strict_s.get("config_ok") is not True
    ):
        errors.append(
            "Inconsistent strict summary: "
            "all_ok=true but config_ok!=true"
        )

    return errors, warnings


def main() -> int:
    args = parse_args()
    base_path = Path(args.base)
    strict_path = Path(args.strict)

    errors: list[str] = []
    warnings: list[str] = []

    if not base_path.exists():
        errors.append(f"Missing base artifact: {base_path}")
    if not strict_path.exists():
        errors.append(f"Missing strict artifact: {strict_path}")

    base_payload: dict[str, Any] = {}
    strict_payload: dict[str, Any] = {}

    if not errors:
        try:
            base_payload = load_json(base_path)
        except json.JSONDecodeError:
            errors.append(f"Invalid JSON in base artifact: {base_path}")
        try:
            strict_payload = load_json(strict_path)
        except json.JSONDecodeError:
            errors.append(f"Invalid JSON in strict artifact: {strict_path}")

    if not errors:
        cmp_errors, cmp_warnings = compare(base_payload, strict_payload)
        errors.extend(cmp_errors)
        warnings.extend(cmp_warnings)

    if args.json:
        print(
            json.dumps(
                {
                    "summary": {
                        "all_ok": len(errors) == 0,
                        "errors": len(errors),
                        "warnings": len(warnings),
                    },
                    "errors": errors,
                    "warnings": warnings,
                    "base": str(base_path),
                    "strict": str(strict_path),
                },
                indent=2,
            )
        )
    else:
        print(f"base={base_path}")
        print(f"strict={strict_path}")
        for w in warnings:
            print(f"WARN: {w}")
        for e in errors:
            print(f"ERROR: {e}")
        print("status=OK" if not errors else "status=FAIL")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
