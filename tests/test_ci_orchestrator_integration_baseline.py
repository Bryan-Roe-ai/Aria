"""Unit tests for CI orchestrator integration baseline flow."""

from __future__ import annotations

import pytest

import scripts.ci_orchestrator as ci_module


@pytest.mark.unit
def test_run_integration_baseline_executes_expected_step_order() -> None:
    ci = ci_module.CIOrchestrator()
    calls: list[str] = []

    ci.validate_all_orchestrators = lambda: calls.append("validate_all") or True
    ci.run_integration_smoke = lambda: calls.append("integration_smoke") or True
    ci.run_integration_contract_tests = lambda: calls.append("contract_tests") or True
    ci.run_targeted_provider_regression = lambda: calls.append("targeted_regression") or True

    ok = ci.run_integration_baseline()

    assert ok is True
    assert calls == [
        "validate_all",
        "integration_smoke",
        "contract_tests",
        "targeted_regression",
    ]


@pytest.mark.unit
def test_run_integration_baseline_reports_failure_when_any_step_fails() -> None:
    ci = ci_module.CIOrchestrator()

    ci.validate_all_orchestrators = lambda: True
    ci.run_integration_smoke = lambda: False
    ci.run_integration_contract_tests = lambda: True
    ci.run_targeted_provider_regression = lambda: True

    ok = ci.run_integration_baseline()

    assert ok is False
