from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_required_files(repo: Path) -> list[CheckResult]:
    required = [
        "data_out/run_pr_review_eval_report.py",
        "data_out/run_pr_review_eval_report_latest.py",
        "data_out/list_pr_review_eval_runs.py",
        "data_out/print_pr_eval_status.py",
        "data_out/generate_mock_pr_review_eval_result.py",
        "scripts/validate_eval_artifacts.py",
    ]
    results: list[CheckResult] = []
    for rel in required:
        p = repo / rel
        results.append(
            CheckResult(
                name=f"file:{rel}",
                ok=p.exists(),
                detail="present" if p.exists() else "missing",
            )
        )
    return results


def check_make_targets(repo: Path) -> list[CheckResult]:
    makefile = (repo / "Makefile").read_text(encoding="utf-8")
    targets = [
        "pr-eval-report:",
        "pr-eval-report-latest:",
        "pr-eval-gate:",
        "pr-eval-gate-latest:",
        "pr-eval-mock:",
        "pr-eval-list:",
        "pr-eval-status:",
        "pr-eval-triage-latest:",
        "pr-eval-all:",
        "pr-eval-all-strict:",
        "validate-eval-workflow-setup:",
        "validate-eval-workflow-setup-json:",
        "validate-eval-artifacts:",
        "validate-eval-artifacts-json:",
    ]
    return [
        CheckResult(
            name=f"make:{t[:-1]}",
            ok=t in makefile,
            detail="found" if t in makefile else "missing",
        )
        for t in targets
    ]


def check_vscode_tasks(repo: Path) -> list[CheckResult]:
    tasks_file = repo / ".vscode/tasks.json"
    if not tasks_file.exists():
        return [CheckResult("tasks:file", False, "missing .vscode/tasks.json")]

    obj = load_json(tasks_file)
    labels = {t.get("label") for t in obj.get("tasks", []) if isinstance(t, dict) and isinstance(t.get("label"), str)}

    required = [
        "eval: pr-report",
        "eval: pr-report-latest",
        "eval: pr-gate",
        "eval: pr-gate-latest",
        "eval: pr-mock",
        "eval: pr-list-runs",
        "eval: pr-status",
        "eval: pr-triage-latest",
        "eval: pr-all",
        "eval: pr-all-strict",
        "validate: eval-workflow-setup",
        "validate: eval-workflow-setup-json",
        "validate: eval-artifacts",
        "validate: eval-artifacts-json",
    ]

    return [
        CheckResult(
            name=f"task:{label}",
            ok=label in labels,
            detail="found" if label in labels else "missing",
        )
        for label in required
    ]


def print_results(results: list[CheckResult]) -> int:
    failures = [r for r in results if not r.ok]
    for r in results:
        status = "OK" if r.ok else "FAIL"
        print(f"{status:4} {r.name} - {r.detail}")

    print("---")
    ok_count = len(results) - len(failures)
    print(f"total={len(results)} ok={ok_count} fail={len(failures)}")
    return 1 if failures else 0


def print_results_json(results: list[CheckResult]) -> int:
    failures = [r for r in results if not r.ok]
    payload = {
        "summary": {
            "total": len(results),
            "ok": len(results) - len(failures),
            "fail": len(failures),
            "all_ok": len(failures) == 0,
        },
        "checks": [{"name": r.name, "ok": r.ok, "detail": r.detail} for r in results],
    }
    print(json.dumps(payload, indent=2))
    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PR eval workflow wiring.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(__file__).resolve().parents[1]
    results: list[CheckResult] = []
    results.extend(check_required_files(repo))
    results.extend(check_make_targets(repo))
    results.extend(check_vscode_tasks(repo))
    if args.json:
        return print_results_json(results)
    return print_results(results)


if __name__ == "__main__":
    raise SystemExit(main())
