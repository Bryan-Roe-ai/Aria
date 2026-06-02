"""Validator — run lint / tests after executor changes.

The validator is best-effort: if a tool is missing it returns success with
a note, rather than blocking the loop. The orchestrator decides how to
react to validation results (e.g., revert and skip commit).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

_logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Aggregate result of all validation steps."""

    ok: bool
    steps: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"ok": self.ok, "steps": list(self.steps)}


@dataclass
class Validator:
    """Run lightweight repository checks after applying changes."""

    repo_root: Path
    timeout_seconds: int = 120

    def validate(self, changed_paths: Sequence[Path] | None = None) -> ValidationResult:
        steps: list[dict] = []
        ok = True

        ruff_step = self._run_ruff(changed_paths)
        steps.append(ruff_step)
        if ruff_step["status"] == "failed":
            ok = False

        black_step = self._run_black(changed_paths)
        steps.append(black_step)
        if black_step["status"] == "failed":
            ok = False

        return ValidationResult(ok=ok, steps=steps)

    # ------------------------------------------------------------------
    def _run_ruff(self, changed_paths: Sequence[Path] | None) -> dict:
        ruff = shutil.which("ruff")
        if not ruff:
            return {
                "name": "ruff",
                "status": "skipped",
                "reason": "ruff binary not found on PATH",
            }

        targets: list[str]
        if changed_paths is not None:
            targets = [str(p) for p in changed_paths if p.suffix == ".py"]
            if not targets:
                return {
                    "name": "ruff",
                    "status": "skipped",
                    "reason": "no python files in changeset",
                }
        else:
            targets = ["."]

        cmd = [ruff, "check", *targets]
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"name": "ruff", "status": "failed", "reason": "ruff timed out"}
        except OSError as exc:  # pragma: no cover - environment dependent
            return {"name": "ruff", "status": "skipped", "reason": f"ruff not runnable: {exc}"}

        status = "passed" if proc.returncode == 0 else "failed"
        return {
            "name": "ruff",
            "status": status,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }

    def _run_black(self, changed_paths: Sequence[Path] | None) -> dict:
        black = shutil.which("black")
        if not black:
            return {
                "name": "black",
                "status": "skipped",
                "reason": "black binary not found on PATH",
            }

        targets: list[str]
        if changed_paths is not None:
            targets = [str(p) for p in changed_paths if p.suffix == ".py"]
            if not targets:
                return {
                    "name": "black",
                    "status": "skipped",
                    "reason": "no python files in changeset",
                }
        else:
            targets = ["."]

        # Use repo config (pyproject.toml) if available, otherwise just --check.
        cmd = [black, "--check", "--quiet", *targets]
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"name": "black", "status": "failed", "reason": "black timed out"}
        except OSError as exc:  # pragma: no cover - environment dependent
            return {"name": "black", "status": "skipped", "reason": f"black not runnable: {exc}"}

        status = "passed" if proc.returncode == 0 else "failed"
        return {
            "name": "black",
            "status": status,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }
