"""Aria Bot — autonomous, deterministic repository self-improvement.

This package implements the self-modifying codebase mode scaffolded in
``aria-bot/README.md``. It is intentionally **rules-based and deterministic**;
it does not call any LLM. For LLM-driven, task-based work see
``scripts/autonomous_code_agent.py`` instead.

Safety guarantees (enforced by :mod:`aria_bot.risk_manager`):

* Dry-run by default; ``--apply`` is required to write to disk.
* Never pushes to a remote; commits stay local.
* Only whitelisted, idempotent text transforms are applied: UTF-8 BOM
  stripping, trailing whitespace, missing-final-newline, trailing-blank-lines,
  and CRLF/lone-CR→LF line-ending normalization.
* Protected paths (``datasets/``, ``.git/``, ``.github/agents/``,
  ``local.settings.json``, ``data_out/``) are never modified.
* Per-cycle file and plan limits prevent runaway changes.
"""

from __future__ import annotations

from .analyzer import Analyzer, Finding
from .commit_system import CommitSystem
from .defaults import DEFAULT_MAX_PLANS
from .executor import ExecutionResult, Executor
from .orchestrator import Orchestrator, OrchestratorConfig, run_cycle
from .planner import Planner, UpgradePlan
from .registry import SUPPORTED_FINDING_KINDS
from .risk_manager import RiskAssessment, RiskManager
from .validator import ValidationResult, Validator

__all__ = [
    "Analyzer",
    "Finding",
    "CommitSystem",
    "DEFAULT_MAX_PLANS",
    "Executor",
    "ExecutionResult",
    "Orchestrator",
    "OrchestratorConfig",
    "SUPPORTED_FINDING_KINDS",
    "run_cycle",
    "Planner",
    "UpgradePlan",
    "RiskAssessment",
    "RiskManager",
    "Validator",
    "ValidationResult",
]
