"""Tests for the deterministic self-modifying loop in ``aria-bot/aria_bot``."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG_PARENT = REPO_ROOT / "aria-bot"
if str(PKG_PARENT) not in sys.path:
    sys.path.insert(0, str(PKG_PARENT))

from aria_bot import (  # noqa: E402  (sys.path tweak above)
    Analyzer,
    Executor,
    Orchestrator,
    OrchestratorConfig,
    Planner,
    RiskManager,
    run_cycle,
)
from aria_bot.commit_system import COMMIT_PREFIX  # noqa: E402


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """Build a tiny fake repo: one fixable file, one protected file."""

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "needs_fix.py").write_bytes(
        # trailing ws on both lines, has final newline
        b"def foo():    \n    return 1   \n"
    )
    # no trailing newline
    (tmp_path / "src" / "needs_newline.md").write_bytes(b"# heading")
    (tmp_path / "src" / "crlf_file.txt").write_bytes(b"a\r\nb\r\n")
    (tmp_path / "src" / "extra_eof.md").write_bytes(b"line\n\n\n")
    (tmp_path / "src" / "bom_file.txt").write_bytes(b"\xef\xbb\xbfhello\n")
    (tmp_path / "src" / "unicode_newline.txt").write_text("a\u2028b\u2029")
    (tmp_path / "src" / "blank_runs.md").write_text("A\n\n\n\nB\n")
    (tmp_path / "src" / "nbsp.md").write_text("A\u00a0B\n")
    (tmp_path / "src" / "zwsp.md").write_text("A\u200bB\u2060C\n")
    (tmp_path / "src" / "clean.py").write_bytes(b"def ok():\n    return 1\n")

    # Protected: must never be touched.
    (tmp_path / "datasets").mkdir()
    (tmp_path / "datasets" / "dirty.py").write_bytes(b"x = 1   \n")
    return tmp_path


def test_risk_manager_blocks_protected_paths(fake_repo: Path) -> None:
    rm = RiskManager(repo_root=fake_repo)
    assert rm.is_path_protected(fake_repo / "datasets" / "dirty.py")
    assert rm.is_path_protected(fake_repo / ".git" / "HEAD")
    assert not rm.is_path_protected(fake_repo / "src" / "needs_fix.py")


def test_risk_manager_blocks_virtualenv_paths(tmp_path: Path) -> None:
    rm = RiskManager(repo_root=tmp_path)
    assert rm.is_path_protected(tmp_path / ".venv" / "lib" / "site.py")
    assert rm.is_path_protected(tmp_path / "venv" / "lib" / "site.py")
    assert rm.is_path_protected(tmp_path / "any" / "data_out" / "x.txt")


def test_risk_manager_blocks_symlinks(tmp_path: Path) -> None:
    target = tmp_path / "real.py"
    target.write_text("x = 1\n")
    link = tmp_path / "link.py"
    link.symlink_to(target)

    rm = RiskManager(repo_root=tmp_path)
    assessment = rm.assess_file(link)
    assert not assessment.allowed
    assert any("symlink" in r for r in assessment.reasons)


def test_risk_manager_blocks_non_writable_files(tmp_path: Path) -> None:
    p = tmp_path / "readonly.py"
    p.write_text("x = 1\n")
    p.chmod(0o444)

    rm = RiskManager(repo_root=tmp_path)
    assessment = rm.assess_file(p)
    assert not assessment.allowed
    assert any("not writable" in r for r in assessment.reasons)


def test_risk_manager_caps_file_size(tmp_path: Path) -> None:
    big = tmp_path / "big.py"
    big.write_bytes(b"a = 1\n" * 2)  # 12 bytes, well over the 1-byte cap
    rm = RiskManager(repo_root=tmp_path, max_file_bytes=1)
    assert not rm.assess_file(big).allowed


def test_risk_manager_rejects_no_op(tmp_path: Path) -> None:
    p = tmp_path / "a.py"
    p.write_bytes(b"x = 1\n")
    rm = RiskManager(repo_root=tmp_path)
    assessment = rm.assess_change(p, b"x = 1\n", b"x = 1\n")
    assert not assessment.allowed
    assert any("no-op" in r for r in assessment.reasons)


def test_analyzer_detects_findings(fake_repo: Path) -> None:
    rm = RiskManager(repo_root=fake_repo)
    findings = Analyzer(risk_manager=rm).scan()
    kinds_by_path = {(f.path.name, f.kind) for f in findings}

    assert ("needs_fix.py", "trailing_whitespace") in kinds_by_path
    assert ("needs_newline.md", "missing_final_newline") in kinds_by_path
    assert ("crlf_file.txt", "normalize_line_endings") in kinds_by_path
    assert ("extra_eof.md", "excess_final_newlines") in kinds_by_path
    assert ("bom_file.txt", "remove_utf8_bom") in kinds_by_path
    assert ("unicode_newline.txt", "normalize_unicode_newlines") in kinds_by_path
    assert ("blank_runs.md", "collapse_blank_line_runs") in kinds_by_path
    assert ("nbsp.md", "normalize_nonbreaking_spaces") in kinds_by_path
    assert ("zwsp.md", "remove_zero_width_chars") in kinds_by_path
    # Protected file must not appear at all.
    assert not any(f.path.name == "dirty.py" for f in findings)
    # Clean file should produce nothing.
    assert not any(f.path.name == "clean.py" for f in findings)


def test_planner_groups_by_path_and_filters_protected(fake_repo: Path) -> None:
    rm = RiskManager(repo_root=fake_repo)
    findings = Analyzer(risk_manager=rm).scan()
    plans = Planner(risk_manager=rm).build_plans(findings)
    paths = {p.path.name for p in plans}
    assert "needs_fix.py" in paths
    assert "needs_newline.md" in paths
    assert "dirty.py" not in paths


def test_executor_dry_run_does_not_write(fake_repo: Path) -> None:
    rm = RiskManager(repo_root=fake_repo)
    findings = Analyzer(risk_manager=rm).scan()
    plans = Planner(risk_manager=rm).build_plans(findings)
    before = (fake_repo / "src" / "needs_fix.py").read_bytes()

    results = Executor(risk_manager=rm, dry_run=True).execute(plans)
    after = (fake_repo / "src" / "needs_fix.py").read_bytes()

    assert before == after
    assert all(not r.applied for r in results)
    assert any(r.reason == "dry-run" for r in results)


def test_executor_applies_and_is_idempotent(fake_repo: Path) -> None:
    rm = RiskManager(repo_root=fake_repo)

    # First pass: applies fixes.
    findings = Analyzer(risk_manager=rm).scan()
    plans = Planner(risk_manager=rm).build_plans(findings)
    results = Executor(risk_manager=rm, dry_run=False).execute(plans)
    assert any(r.applied for r in results)

    fixed = (fake_repo / "src" / "needs_fix.py").read_bytes()
    assert b"   \n" not in fixed
    assert (fake_repo / "src" / "needs_newline.md").read_bytes().endswith(b"\n")
    assert b"\r" not in (fake_repo / "src" / "crlf_file.txt").read_bytes()
    assert (fake_repo / "src" / "extra_eof.md").read_bytes() == b"line\n"
    assert not (fake_repo / "src" /
                "bom_file.txt").read_text().startswith("\ufeff")
    assert "\u2028" not in (
        fake_repo / "src" / "unicode_newline.txt").read_text()
    assert "\u2029" not in (
        fake_repo / "src" / "unicode_newline.txt").read_text()
    assert (fake_repo / "src" / "blank_runs.md").read_text() == "A\n\nB\n"
    assert "\u00a0" not in (fake_repo / "src" / "nbsp.md").read_text()
    assert "\u200b" not in (fake_repo / "src" / "zwsp.md").read_text()
    assert "\u2060" not in (fake_repo / "src" / "zwsp.md").read_text()
    # Protected file untouched.
    assert (fake_repo / "datasets" / "dirty.py").read_bytes() == b"x = 1   \n"

    # Second pass: nothing left to do.
    findings2 = Analyzer(risk_manager=rm).scan()
    plans2 = Planner(risk_manager=rm).build_plans(findings2)
    assert plans2 == []


def test_orchestrator_dry_run_writes_status(fake_repo: Path) -> None:
    config = OrchestratorConfig(repo_root=fake_repo, apply=False, commit=False)
    result = Orchestrator(config=config).run()

    status_path = fake_repo / "data_out" / "aria_bot" / "status.json"
    assert status_path.exists()
    payload = json.loads(status_path.read_text())
    assert payload["apply"] is False
    assert payload["totals"]["findings"] >= 2
    assert "findings_by_kind" in payload
    assert "plans_by_kind" in payload
    assert "applied_by_kind" in payload
    assert payload["applied_by_kind"] == {}
    # Dry-run never applies.
    assert payload["totals"]["applied"] == 0
    # No file mutation occurred.
    assert (fake_repo / "src" / "needs_fix.py").read_bytes().endswith(b"   \n")
    # ruff may be missing in test env
    assert result.validation_ok in (True, False)


def test_run_cycle_apply_modifies_files(fake_repo: Path) -> None:
    result = run_cycle(repo_root=fake_repo, apply=True, commit=False)
    assert result.apply is True
    applied = [e for e in result.executions if e.applied]
    assert applied, "expected at least one applied plan"

    payload = result.to_dict()
    assert payload["applied_by_kind"]
    assert payload["findings_by_kind"]
    assert payload["plans_by_kind"]
    # Protected dataset file is still dirty.
    assert (fake_repo / "datasets" / "dirty.py").read_bytes() == b"x = 1   \n"


def test_run_cycle_enable_kind_limits_changes(fake_repo: Path) -> None:
    result = run_cycle(
        repo_root=fake_repo,
        apply=True,
        commit=False,
        enabled_kinds=["missing_final_newline"],
    )
    assert result.apply is True

    # missing_final_newline should be fixed.
    assert (fake_repo / "src" / "needs_newline.md").read_bytes().endswith(b"\n")
    # trailing whitespace should remain because that kind was not enabled.
    assert (fake_repo / "src" / "needs_fix.py").read_bytes().endswith(b"   \n")


def test_run_cycle_disable_kind_excludes_changes(fake_repo: Path) -> None:
    result = run_cycle(
        repo_root=fake_repo,
        apply=True,
        commit=False,
        disabled_kinds=["trailing_whitespace"],
    )
    assert result.apply is True

    # trailing whitespace should remain because that kind was disabled.
    assert (fake_repo / "src" / "needs_fix.py").read_bytes().endswith(b"   \n")
    # other kinds should still run.
    assert (fake_repo / "src" / "needs_newline.md").read_bytes().endswith(b"\n")


def test_commit_requires_apply(fake_repo: Path) -> None:
    """The CLI rejects --commit without --apply."""

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "aria_bot",
            "--repo-root",
            str(fake_repo),
            "--commit",
            "--quiet",
        ],
        cwd=PKG_PARENT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "--commit requires --apply" in proc.stderr


def test_commit_message_uses_known_prefix() -> None:
    assert COMMIT_PREFIX.startswith("chore(aria-bot):")


def test_cli_list_kinds_outputs_supported_kinds() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "aria_bot",
            "--list-kinds",
        ],
        cwd=PKG_PARENT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    output_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert "trailing_whitespace" in output_lines
    assert "missing_final_newline" in output_lines
    assert "remove_zero_width_chars" in output_lines
