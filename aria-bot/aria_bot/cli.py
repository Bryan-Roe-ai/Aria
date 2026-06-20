"""Command-line interface for the Aria self-modifying loop.

Run a single cycle with::

    python -m aria_bot                 # dry-run, no writes
    python -m aria_bot --apply         # write fixes to disk (no commit)
    python -m aria_bot --apply --commit  # also create a local git commit
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

from .analyzer import SUPPORTED_KINDS
from .orchestrator import run_cycle


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aria_bot",
        description="Run one self-modifying repository cycle (rules-based, deterministic).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to operate on (default: current working directory).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write fixes to disk. Without this flag the run is dry-run.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Create a local git commit for applied changes (requires --apply).",
    )
    parser.add_argument(
        "--max-plans",
        type=int,
        default=50,
        help="Cap on the number of plans applied per cycle.",
    )
    parser.add_argument(
        "--enable-kind",
        action="append",
        choices=SUPPORTED_KINDS,
        default=None,
        help=(
            "Only run the specified finding kind(s). "
            "Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--disable-kind",
        action="append",
        choices=SUPPORTED_KINDS,
        default=None,
        help=(
            "Skip the specified finding kind(s). "
            "Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--status-path",
        type=Path,
        default=None,
        help="Override the status.json output location.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the JSON summary (status file is still written).",
    )
    parser.add_argument(
        "--output-format",
        choices=("json", "compact"),
        default="json",
        help=(
            "Summary output format: pretty JSON ('json') or single-line "
            "JSON ('compact')."
        ),
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=None,
        help="Optional path to also write the CLI summary JSON.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO).",
    )
    parser.add_argument(
        "--list-kinds",
        action="store_true",
        help="List supported finding/transform kinds and exit.",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help=(
            "Exit with status 1 when any findings are detected "
            "(useful for CI quality gates)."
        ),
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        default=None,
        help=(
            "Exit with status 1 when findings exceed this threshold "
            "(useful for CI budgets)."
        ),
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_kinds:
        for kind in SUPPORTED_KINDS:
            print(kind)
        return 0

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.commit and not args.apply:
        print("error: --commit requires --apply", file=sys.stderr)
        return 2

    result = run_cycle(
        repo_root=args.repo_root,
        apply=args.apply,
        commit=args.commit,
        max_plans=args.max_plans,
        status_path=args.status_path,
        enabled_kinds=args.enable_kind,
        disabled_kinds=args.disable_kind,
    )

    result_dict = result.to_dict()
    summary = {
        "totals": result_dict["totals"],
        "findings_by_kind": result_dict["findings_by_kind"],
        "plans_by_kind": result_dict["plans_by_kind"],
        "applied_by_kind": result_dict["applied_by_kind"],
        "validation_ok": result.validation_ok,
        "commit_sha": result.commit_sha,
        "notes": result.notes,
        "apply": result.apply,
        "commit": result.commit,
    }

    if args.output_format == "compact":
        rendered = json.dumps(summary, sort_keys=True)
    else:
        rendered = json.dumps(summary, indent=2, sort_keys=True)

    if args.summary_path is not None:
        args.summary_path.parent.mkdir(parents=True, exist_ok=True)
        args.summary_path.write_text(rendered + "\n", encoding="utf-8")

    if not args.quiet:
        sys.stdout.write(rendered)
        sys.stdout.write("\n")

    if args.fail_on_findings and result_dict["totals"]["findings"] > 0:
        return 1

    if args.max_findings is not None:
        if args.max_findings < 0:
            print("error: --max-findings must be >= 0", file=sys.stderr)
            return 2
        if result_dict["totals"]["findings"] > args.max_findings:
            return 1

    return 0 if result.validation_ok else 1


if __name__ == "__main__":  # pragma: no cover - module entrypoint
    raise SystemExit(main())
