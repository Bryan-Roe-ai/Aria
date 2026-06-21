#!/usr/bin/env python3
"""Run all registered repository automation agents.

Each agent inspects the repository and writes structured results to
``data_out/agents/<agent-name>/status.json``. This runner executes every
registered agent, aggregates the outcomes, and persists a summary at
``data_out/agents/status.json``.

Examples:
  python scripts/run_repo_agents.py
  python scripts/run_repo_agents.py --json
  python scripts/run_repo_agents.py --agent status-freshness --dry-run
  python scripts/run_repo_agents.py --fail-on-warning
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agents.base import (  # noqa: E402
    AGENTS_DATA_DIR,
    AgentResult,
    AutomationAgent,
    get_registered_agents,
    utc_now_iso,
)

# Import agent modules so their @register decorators populate the registry.
_AGENT_MODULES = (
    "scripts.agents.status_freshness_agent",
    "scripts.agents.marker_audit_agent",
    "scripts.agents.docstring_audit_agent",
    "scripts.agents.agents_md_audit_agent",
)

SUMMARY_PATH = AGENTS_DATA_DIR / "status.json"


@dataclass
class RunSummary:
    generated_at: str
    agents_run: int
    ok: int
    warning: int
    error: int
    results: list[dict]
    succeeded: bool


def _load_agents() -> dict[str, type[AutomationAgent]]:
    for module_name in _AGENT_MODULES:
        importlib.import_module(module_name)
    return get_registered_agents()


def _aggregate_status(results: list[AgentResult]) -> str:
    if any(result.status == "error" for result in results):
        return "error"
    if any(result.status == "warning" for result in results):
        return "warning"
    return "ok"


def run_agents(
    *,
    selected: Sequence[str] | None = None,
    dry_run: bool = False,
) -> tuple[list[AgentResult], RunSummary]:
    registry = _load_agents()
    names = sorted(selected) if selected else sorted(registry)
    missing = [name for name in names if name not in registry]
    if missing:
        raise SystemExit(f"Unknown agent(s): {', '.join(missing)}")

    results: list[AgentResult] = []
    for name in names:
        agent = registry[name]()
        result = agent.run()
        results.append(result)
        if not dry_run:
            agent.write_status(result)
        print(f"[{result.status}] {name}: {result.summary}")

    counts = {"ok": 0, "warning": 0, "error": 0}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    summary = RunSummary(
        generated_at=utc_now_iso(),
        agents_run=len(results),
        ok=counts["ok"],
        warning=counts["warning"],
        error=counts["error"],
        results=[result.to_dict() for result in results],
        succeeded=_aggregate_status(results) == "ok",
    )
    return results, summary


def write_summary(summary: RunSummary) -> Path:
    AGENTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
    return SUMMARY_PATH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run repository automation agents.")
    parser.add_argument(
        "--agent",
        action="append",
        dest="agents",
        help="Run only the named agent (repeatable). Default: all registered agents.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute agent results without writing per-agent status files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the aggregated summary as JSON.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with code 1 when any agent reports error status.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with code 1 when any agent reports warning or error.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _, summary = run_agents(selected=args.agents, dry_run=args.dry_run)

    if not args.dry_run:
        path = write_summary(summary)
        print(f"[run_repo_agents] summary written to {path}")

    if args.json:
        print(json.dumps(asdict(summary), indent=2))

    if args.fail_on_error and summary.error:
        return 1
    if args.fail_on_warning and (summary.warning or summary.error):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
