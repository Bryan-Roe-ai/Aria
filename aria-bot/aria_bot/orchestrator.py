"""Orchestrator — run a single self-modification cycle end-to-end.

Execution flow (matches ``aria-bot/README.md``):

1. Analyze repository state.
2. Generate improvement plan.
3. Execute safe changes (or simulate, in dry-run).
4. Validate results.
5. Commit changes (only when ``apply`` and ``commit`` are both enabled).

Every cycle writes a machine-readable status file to
``data_out/aria_bot/status.json`` so dashboards and other orchestrators
can observe progress (per the repo's status.json convention).
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .analyzer import Analyzer, Finding
from .commit_system import CommitSystem
from .executor import ExecutionResult, Executor
from .planner import Planner, UpgradePlan
from .risk_manager import RiskManager
from .validator import Validator

_logger = logging.getLogger(__name__)

# The orchestrator is stateless across runs but always writes its status
# to the same well-known location for observability.
_DEFAULT_STATUS_PATH = Path("data_out") / "aria_bot" / "status.json"


@dataclass
class OrchestratorConfig:
    """User-facing knobs for one cycle."""

    repo_root: Path
    apply: bool = False
    commit: bool = False
    max_plans: int = 50
    status_path: Path | None = None
    paths: Sequence[Path] | None = None

    def resolve_status_path(self) -> Path:
        if self.status_path is not None:
            return Path(self.status_path)
        return Path(self.repo_root) / _DEFAULT_STATUS_PATH


@dataclass
class CycleResult:
    """Aggregated outcome of one cycle, ready to serialize."""

    started_at: str
    finished_at: str
    duration_seconds: float
    apply: bool
    commit: bool
    findings: list[Finding] = field(default_factory=list)
    plans: list[UpgradePlan] = field(default_factory=list)
    executions: list[ExecutionResult] = field(default_factory=list)
    validation_ok: bool = True
    validation: dict = field(default_factory=dict)
    commit_sha: str | None = None
    notes: list[str] = field(default_factory=list)

    def _state(self, applied: list[ExecutionResult], skipped: list[ExecutionResult]) -> str:
        if not self.apply:
            return "dry_run"
        if self.validation_ok is False:
            return "validation_failed"
        if applied:
            return "applied"
        if skipped and not applied:
            return "no_changes"
        return "idle"

    def to_dict(self) -> dict:
        applied = [e for e in self.executions if e.applied]
        skipped = [e for e in self.executions if not e.applied]
        applied_paths = [str(e.plan.path) for e in applied]
        skipped_paths = [str(e.plan.path) for e in skipped]
        validation_targets = applied_paths if applied_paths else []

        finding_kinds: dict[str, int] = {}
        for finding in self.findings:
            finding_kinds[finding.kind] = finding_kinds.get(finding.kind, 0) + 1

        plan_kinds: dict[str, int] = {}
        for plan in self.plans:
            for kind in plan.kinds:
                plan_kinds[kind] = plan_kinds.get(kind, 0) + 1

        def _format_kind_summary(kind_counts: dict[str, int]) -> str:
            if not kind_counts:
                return "none"
            return ", ".join(f"{kind}={count}" for kind, count in sorted(kind_counts.items()))

        counts = {
            "findings": len(self.findings),
            "plans": len(self.plans),
            "executions": len(self.executions),
            "applied": len(applied),
            "skipped": len(skipped),
        }

        state = self._state(applied, skipped)
        status_text = (
            f"{state}: {counts['findings']} finding(s), {counts['plans']} plan(s), "
            f"{counts['applied']} applied, {counts['skipped']} skipped"
        )

        summary = {
            "state": state,
            "status_text": status_text,
            "counts": counts,
            "paths": {
                "applied": applied_paths,
                "skipped": skipped_paths,
                "validated": validation_targets,
            },
            "by_kind": {
                "findings": finding_kinds,
                "plans": plan_kinds,
            },
            "kind_summary": {
                "findings": _format_kind_summary(finding_kinds),
                "plans": _format_kind_summary(plan_kinds),
            },
        }

        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 3),
            "apply": self.apply,
            "commit": self.commit,
            "totals": {
                "findings": len(self.findings),
                "plans": len(self.plans),
                "executions": len(self.executions),
                "applied": len(applied),
                "skipped": len(skipped),
            },
            "findings": [f.to_dict() for f in self.findings],
            "plans": [p.to_dict() for p in self.plans],
            "executions": [e.to_dict() for e in self.executions],
            "status_text": status_text,
            "applied_paths": applied_paths,
            "skipped_paths": skipped_paths,
            "validation_targets": validation_targets,
            "summary": summary,
            "validation_ok": self.validation_ok,
            "validation": self.validation,
            "commit_sha": self.commit_sha,
            "notes": list(self.notes),
        }


@dataclass
class Orchestrator:
    """Wire the modules together for a single cycle."""

    config: OrchestratorConfig

    def run(self) -> CycleResult:
        started = time.monotonic()
        started_iso = datetime.now(timezone.utc).isoformat()

        repo_root = Path(self.config.repo_root).resolve()
        risk = RiskManager(repo_root=repo_root)
        analyzer = Analyzer(risk_manager=risk)
        planner = Planner(risk_manager=risk, max_plans=self.config.max_plans)
        executor = Executor(risk_manager=risk, dry_run=not self.config.apply)
        validator = Validator(repo_root=repo_root)
        commits = CommitSystem(repo_root=repo_root)

        notes: list[str] = []

        _logger.info("aria-bot: scanning repository at %s", repo_root)
        scan_paths = self._resolve_paths(analyzer) if self.config.paths else None
        findings = analyzer.scan(paths=scan_paths)
        _logger.info("aria-bot: %d finding(s)", len(findings))

        plans = planner.build_plans(findings)
        _logger.info("aria-bot: %d plan(s) after risk filter", len(plans))

        executions = executor.execute(plans)
        applied_paths = [e.plan.path for e in executions if e.applied]
        skipped_paths = [e.plan.path for e in executions if not e.applied]

        # Only validate when files were actually modified — dry-runs and
        # no-op cycles have nothing to validate.
        if applied_paths:
            validation = validator.validate(applied_paths)
        else:
            validation = validator.validate(changed_paths=[])
        notes.append(
            f"execution summary: {len(executions)} plan(s), {len(applied_paths)} applied, {len(skipped_paths)} skipped"
        )
        if not validation.ok:
            notes.append("validation failed; skipping commit")
        elif applied_paths:
            notes.append(f"validated {len(applied_paths)} applied path(s)")

        commit_sha: str | None = None
        if self.config.apply and self.config.commit and validation.ok and applied_paths:
            message = self._commit_message(executions)
            commit_sha = commits.commit(applied_paths, message)
            if commit_sha is None:
                notes.append("commit step produced no SHA (nothing staged or git unavailable)")
        elif not self.config.apply:
            notes.append("dry-run: no files were modified")
        elif not applied_paths:
            notes.append("no plans were applied")

        finished = time.monotonic()
        finished_iso = datetime.now(timezone.utc).isoformat()
        result = CycleResult(
            started_at=started_iso,
            finished_at=finished_iso,
            duration_seconds=finished - started,
            apply=self.config.apply,
            commit=self.config.commit,
            findings=findings,
            plans=plans,
            executions=executions,
            validation_ok=validation.ok,
            validation=validation.to_dict(),
            commit_sha=commit_sha,
            notes=notes,
        )
        self._write_status(result)
        return result

    # ------------------------------------------------------------------
    def _resolve_paths(self, analyzer: Analyzer) -> list[Path]:
        """Expand ``config.paths`` — directories become their matching files."""
        repo_root = Path(self.config.repo_root).resolve()
        result: list[Path] = []
        wanted = {s.lower() for s in analyzer.suffixes}
        for p in self.config.paths or []:
            p = Path(p)
            if not p.is_absolute():
                p = repo_root / p
            if p.is_dir():
                import os

                for root, _dirs, files in os.walk(p):
                    for name in files:
                        fp = Path(root, name)
                        if fp.suffix.lower() in wanted:
                            result.append(fp)
            elif p.is_file():
                result.append(p)
            else:
                _logger.debug("--paths target does not exist: %s", p)
        return result

    def _commit_message(self, executions: list[ExecutionResult]) -> str:
        # Only called when at least one execution applied; defend against
        # accidental misuse by future callers.
        applied = [e for e in executions if e.applied]
        if not applied:
            return "no applied changes"
        kinds: set[str] = set()
        for e in applied:
            kinds.update(e.plan.kinds)
        kind_str = ",".join(sorted(kinds))
        return f"apply {kind_str} to {len(applied)} file(s)"

    def _write_status(self, result: CycleResult) -> None:
        status_path = self.config.resolve_status_path()
        try:
            status_path.parent.mkdir(parents=True, exist_ok=True)
            status_path.write_text(
                json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:  # pragma: no cover - filesystem dependent
            _logger.warning("unable to write status file %s: %s", status_path, exc)


def run_cycle(
    repo_root: Path,
    *,
    apply: bool = False,
    commit: bool = False,
    max_plans: int = 50,
    status_path: Path | None = None,
    paths: Sequence[Path] | None = None,
) -> CycleResult:
    """Convenience wrapper used by the CLI and tests."""

    config = OrchestratorConfig(
        repo_root=Path(repo_root),
        apply=apply,
        commit=commit,
        max_plans=max_plans,
        status_path=status_path,
        paths=list(paths) if paths else None,
    )
    return Orchestrator(config=config).run()
