from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_pair(md_path: Path) -> list[CheckResult]:
    json_path = md_path.with_suffix(".json")
    results: list[CheckResult] = []

    results.append(
        CheckResult(
            name=f"exists:{md_path}",
            ok=md_path.exists(),
            detail="present" if md_path.exists() else "missing",
        )
    )
    results.append(
        CheckResult(
            name=f"exists:{json_path}",
            ok=json_path.exists(),
            detail="present" if json_path.exists() else "missing",
        )
    )

    if not (md_path.exists() and json_path.exists()):
        return results

    try:
        loaded = load_json(json_path)
    except json.JSONDecodeError:
        results.append(
            CheckResult(
                name=f"json_valid:{json_path}",
                ok=False,
                detail="invalid json",
            )
        )
        return results

    report_obj: dict[str, Any]
    if isinstance(loaded, dict):
        report_obj = cast(dict[str, Any], loaded)
    else:
        results.append(
            CheckResult(
                name=f"json_type:{json_path}",
                ok=False,
                detail=f"expected object, got {type(loaded).__name__}",
            )
        )
        return results

    results.append(
        CheckResult(
            name=f"json_valid:{json_path}",
            ok=True,
            detail="valid",
        )
    )

    required_top = [
        "baseline",
        "candidate",
        "metrics",
        "sample_counts",
        "gate",
    ]
    for key in required_top:
        results.append(
            CheckResult(
                name=f"json_key:{json_path}:{key}",
                ok=key in report_obj,
                detail="present" if key in report_obj else "missing",
            )
        )

    gate = report_obj.get("gate")
    results.append(
        CheckResult(
            name=f"gate_value:{json_path}",
            ok=gate in {"BLOCK", "GO_WITH_REVIEW"},
            detail=str(gate),
        )
    )

    samples_raw = report_obj.get("sample_counts", {})
    samples = samples_raw if isinstance(samples_raw, dict) else {}
    base = samples.get("baseline")
    cand = samples.get("candidate")
    results.append(
        CheckResult(
            name=f"sample_counts_type:{json_path}",
            ok=isinstance(base, int) and isinstance(cand, int),
            detail=f"baseline={base} candidate={cand}",
        )
    )

    return results


def print_results(results: list[CheckResult], as_json: bool) -> int:
    fails = [r for r in results if not r.ok]

    if as_json:
        payload = {
            "summary": {
                "total": len(results),
                "ok": len(results) - len(fails),
                "fail": len(fails),
                "all_ok": len(fails) == 0,
            },
            "checks": [{"name": r.name, "ok": r.ok, "detail": r.detail} for r in results],
        }
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            status = "OK" if r.ok else "FAIL"
            print(f"{status:4} {r.name} - {r.detail}")
        print("---")
        ok_count = len(results) - len(fails)
        print(f"total={len(results)} ok={ok_count} fail={len(fails)}")

    return 1 if fails else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated PR eval report artifacts.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Validate latest report artifact pair.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    default = Path("data_out/pr_review_eval_comparison_report.md")
    latest = Path("data_out/pr_review_eval_comparison_report_latest.md")

    targets = [latest] if args.latest else [default, latest]
    results: list[CheckResult] = []
    for t in targets:
        results.extend(validate_pair(t))

    return print_results(results, as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
