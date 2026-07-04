"""Inspect AGI provider import, registry, backends, and canonical paths."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.agents.base import REPO_ROOT, AgentResult, AutomationAgent, register  # noqa: E402

CHAT_CLI_SRC = REPO_ROOT / "ai-projects" / "chat-cli" / "src"
CANONICAL_PROVIDER = CHAT_CLI_SRC / "agi_provider.py"
MIN_REGISTRY_SIZE = 5

CANONICAL_PATHS = (
    CANONICAL_PROVIDER,
    REPO_ROOT / "shared" / "agi_backend_status.py",
    REPO_ROOT / "shared" / "agi_persistence.py",
    REPO_ROOT / "apps" / "aria" / "agi.html",
    REPO_ROOT / "apps" / "aria" / "agi_stream_utils.js",
)


@register
class AgiHealthAgent(AutomationAgent):
    """Verify AGI provider import, agent registry, and backend configuration."""

    name = "agi-health"
    description = "Checks AGI provider import, registry size, backend status, and canonical paths."

    def _relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.repo_root))
        except ValueError:
            return str(path)

    def run(self) -> AgentResult:
        """Run AGI health checks and return structured findings."""
        findings: list[dict] = []
        metrics: dict[str, Any] = {
            "registry_size": 0,
            "provider_import_ok": False,
            "smoke_complete_ok": False,
        }

        for path in CANONICAL_PATHS:
            if not path.exists():
                findings.append(
                    {
                        "issue": "missing_path",
                        "detail": f"Expected AGI artifact not found: {self._relative_path(path)}",
                    }
                )

        provider = None
        registry: dict = {}
        import_error: str | None = None

        if CANONICAL_PROVIDER.exists():
            chat_cli = str(CHAT_CLI_SRC)
            if chat_cli not in sys.path:
                sys.path.insert(0, chat_cli)
            try:
                from agi_provider import _AGENT_REGISTRY, create_agi_provider  # noqa: WPS433

                registry = dict(_AGENT_REGISTRY)
                metrics["registry_size"] = len(registry)
                metrics["provider_import_ok"] = True

                if len(registry) < MIN_REGISTRY_SIZE:
                    findings.append(
                        {
                            "issue": "registry_small",
                            "detail": (
                                f"Agent registry has {len(registry)} entries; expected at least {MIN_REGISTRY_SIZE}."
                            ),
                        }
                    )

                try:
                    provider, info = create_agi_provider(temperature=0.0)
                    metrics["base_provider"] = getattr(info, "name", None) or str(info)
                    response = provider.complete(
                        [{"role": "user", "content": "health ping"}],
                        stream=False,
                    )
                    metrics["smoke_complete_ok"] = bool(str(response).strip())
                except Exception as exc:  # noqa: BLE001 — report smoke failure as finding
                    findings.append(
                        {
                            "issue": "smoke_failed",
                            "detail": f"create_agi_provider/complete smoke check failed: {exc}",
                        }
                    )
            except Exception as exc:  # noqa: BLE001 — report import failure as finding
                import_error = str(exc)
                findings.append(
                    {
                        "issue": "import_failed",
                        "detail": f"Could not import agi_provider from {self._relative_path(CANONICAL_PROVIDER)}: {exc}",
                    }
                )
        else:
            import_error = "canonical provider missing"

        backend_status: dict = {}
        try:
            from shared.agi_backend_status import build_agi_backend_status  # noqa: WPS433

            backend_status = build_agi_backend_status(provider)
            metrics["persistence_type"] = backend_status.get("persistence", {}).get("type")
            metrics["memory_type"] = backend_status.get("memory", {}).get("type")
            if backend_status.get("persistence", {}).get("type") == "none":
                findings.append(
                    {
                        "issue": "persistence_disabled",
                        "detail": "No AGI persistence backend configured (expected for dev; enable via QAI_AGI_PERSIST* env).",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            findings.append(
                {
                    "issue": "backend_status_failed",
                    "detail": f"build_agi_backend_status failed: {exc}",
                }
            )

        error_issues = {"missing_path", "import_failed", "smoke_failed", "backend_status_failed"}
        warning_issues = {"registry_small", "persistence_disabled"}

        if any(f["issue"] in error_issues for f in findings):
            status = "error"
        elif any(f["issue"] in warning_issues for f in findings):
            status = "warning"
        else:
            status = "ok"

        registry_names = sorted(registry) if registry else []
        metrics["registry_agents"] = registry_names
        metrics["backend"] = backend_status
        summary_parts = [
            f"registry={metrics['registry_size']}",
            f"import={'ok' if metrics['provider_import_ok'] else 'fail'}",
            f"smoke={'ok' if metrics['smoke_complete_ok'] else 'fail'}",
        ]
        if import_error and status == "error":
            summary_parts.append(f"error={import_error[:80]}")
        summary = f"AGI health: {', '.join(summary_parts)}; {len(findings)} finding(s)."

        return self.make_result(
            status=status,
            summary=summary,
            findings=findings,
            metrics=metrics,
        )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the AGI health agent."""
    parser = argparse.ArgumentParser(description=AgiHealthAgent.description)
    parser.add_argument("--dry-run", action="store_true", help="Compute results without writing status.json.")
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Return exit code 1 when status is warning or error.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the AGI health CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    agent = AgiHealthAgent()
    result = agent.run()

    if not args.dry_run:
        agent.write_status(result)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.summary)

    if result.status == "error":
        return 1
    if args.fail_on_warning and result.status == "warning":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
