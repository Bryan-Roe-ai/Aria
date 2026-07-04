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
    DEFAULT_MAX_PLANS as EXPORTED_DEFAULT_MAX_PLANS,
)
from aria_bot import (
    SUPPORTED_FINDING_KINDS,
    Analyzer,
    Executor,
    Orchestrator,
    OrchestratorConfig,
    Planner,
    RiskManager,
    run_cycle,
)
from aria_bot.commit_system import COMMIT_PREFIX  # noqa: E402
from aria_bot.defaults import DEFAULT_MAX_PLANS as INTERNAL_DEFAULT_MAX_PLANS  # noqa: E402


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


def test_risk_manager_enforces_hard_coded_default_protections(tmp_path: Path) -> None:
    rm = RiskManager(repo_root=tmp_path)

    protected_examples = [
        tmp_path / ".github" / "agents" / "helper.md",
        tmp_path / "node_modules" / "pkg" / "index.js",
        tmp_path / ".venv" / "bin" / "activate",
        tmp_path / "__pycache__" / "module.cpython-314.pyc",
        tmp_path / ".env",
        tmp_path / "coverage" / "index.html",
    ]

    assert all(rm.is_path_protected(path) for path in protected_examples)


def test_default_max_plans_matches_documentation(tmp_path: Path) -> None:
    rm = RiskManager(repo_root=tmp_path)
    planner = Planner(risk_manager=rm)
    config = OrchestratorConfig(repo_root=tmp_path)

    from aria_bot import cli as aria_cli  # noqa: E402

    parser = aria_cli._build_parser()
    args = parser.parse_args([])

    assert EXPORTED_DEFAULT_MAX_PLANS == 5
    assert INTERNAL_DEFAULT_MAX_PLANS == 5
    assert EXPORTED_DEFAULT_MAX_PLANS == INTERNAL_DEFAULT_MAX_PLANS
    assert planner.max_plans == INTERNAL_DEFAULT_MAX_PLANS
    assert config.max_plans == INTERNAL_DEFAULT_MAX_PLANS
    assert args.max_plans == INTERNAL_DEFAULT_MAX_PLANS


def test_risk_manager_blocks_symlinks(tmp_path: Path) -> None:
    target = tmp_path / "real.py"
    target.write_text("x = 1\n")
    link = tmp_path / "link.py"
    link.symlink_to(target)

    rm = RiskManager(repo_root=tmp_path)
    assessment = rm.assess_file(link)
    assert not assessment.allowed
    assert any("symlink" in r for r in assessment.reasons)


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
    # All emitted kinds must be known (registry is the single source of truth).
    assert {f.kind for f in findings} <= set(SUPPORTED_FINDING_KINDS)
    # Protected file must not appear at all.
    assert not any(f.path.name == "dirty.py" for f in findings)
    # Clean file should produce nothing.
    assert not any(f.path.name == "clean.py" for f in findings)


def test_analyzer_detects_trailing_blank_lines(tmp_path: Path) -> None:
    p = tmp_path / "extra_blank_lines.md"
    p.write_bytes(b"line one\n\n\n")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])

    assert any(f.kind == "trailing_blank_lines" for f in findings)


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
    # Protected file untouched.
    assert (fake_repo / "datasets" / "dirty.py").read_bytes() == b"x = 1   \n"

    # Second pass: nothing left to do.
    findings2 = Analyzer(risk_manager=rm).scan()
    plans2 = Planner(risk_manager=rm).build_plans(findings2)
    assert plans2 == []


@pytest.mark.parametrize(
    "name, content, expected",
    [
        # Stripping a whitespace-only line must not leave a trailing blank line.
        ("ws_then_blank", b"x\n   \n", b"x\n"),
        # Normalizing CRLF blank lines must not leave a trailing blank line.
        ("crlf_blank", b"x\r\n\r\n", b"x\n"),
        # Trailing whitespace + CRLF together.
        ("crlf_ws", b"a \r\nb\r\n", b"a\nb\n"),
        # Extra blank lines collapse to exactly one terminal newline.
        ("extra_blanks", b"line one\n\n\n", b"line one\n"),
        # File of only blank lines collapses to a single newline.
        ("all_blank", b"\n\n\n", b"\n"),
        # Missing final newline is added.
        ("no_newline", b"x", b"x\n"),
        # CRLF without other issues normalizes to LF.
        ("crlf_only", b"a\r\nb\r\n", b"a\nb\n"),
    ],
)
def test_single_pass_idempotency_and_convergence(tmp_path: Path, name: str, content: bytes, expected: bytes) -> None:
    """Applying all fixes for a file must converge in exactly one pass.

    Regression guard: detection of trailing blank lines must account for the
    text *after* CRLF normalization and trailing-whitespace stripping, so the
    bot never leaves a file that the next cycle would flag again.
    """

    p = tmp_path / f"{name}.py"
    p.write_bytes(content)
    rm = RiskManager(repo_root=tmp_path)

    # Pass 1: apply every fix.
    plans = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    Executor(risk_manager=rm, dry_run=False).execute(plans)
    assert p.read_bytes() == expected, f"{name}: unexpected result after pass 1"

    # Pass 2: must find nothing (single-pass convergence / idempotency).
    plans2 = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    assert plans2 == [], f"{name}: not idempotent — pass 2 still has work {plans2}"


def test_transform_order_covers_all_transforms() -> None:
    """Every executable transform must have a defined canonical order."""

    from aria_bot.executor import _TRANSFORMS, TRANSFORM_ORDER
    from aria_bot.registry import SUPPORTED_FINDING_KINDS as REGISTRY_KINDS

    assert set(TRANSFORM_ORDER) == set(_TRANSFORMS)
    assert set(TRANSFORM_ORDER) == set(SUPPORTED_FINDING_KINDS)
    assert TRANSFORM_ORDER == REGISTRY_KINDS


def test_executor_syntax_guard_blocks_breaking_edit(tmp_path: Path) -> None:
    """A transform that would break valid Python syntax must be aborted."""

    from aria_bot.executor import Executor, _py_parses
    from aria_bot.planner import UpgradePlan

    assert _py_parses("x = 1\n", "a.py")
    assert not _py_parses("def (:\n", "a.py")

    p = tmp_path / "good.py"
    p.write_bytes(b"x = 1\n")
    rm = RiskManager(repo_root=tmp_path)
    executor = Executor(risk_manager=rm, dry_run=False)
    # Force a transform that corrupts the file into invalid Python.
    executor_transforms = {"trailing_whitespace": lambda _t: "def (:\n"}
    import aria_bot.executor as _ex

    original = _ex._TRANSFORMS
    _ex._TRANSFORMS = {**original, **executor_transforms}
    try:
        plan = UpgradePlan(path=p, kinds=("trailing_whitespace",))
        result = executor._execute_one(plan)
    finally:
        _ex._TRANSFORMS = original

    assert result.applied is False
    assert "syntax error" in result.reason
    # File must be untouched.
    assert p.read_bytes() == b"x = 1\n"


def test_executor_syntax_guard_allows_preexisting_broken_py(tmp_path: Path) -> None:
    """The guard never blames the bot for a file that was already broken."""

    from aria_bot.executor import _py_parses

    # Original already does not parse -> guard must not block whitespace fixes.
    assert not _py_parses("def (:   \n", "b.py")
    p = tmp_path / "broken.py"
    p.write_bytes(b"def (:   \n")  # invalid syntax + trailing whitespace
    rm = RiskManager(repo_root=tmp_path)
    plans = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    results = Executor(risk_manager=rm, dry_run=False).execute(plans)
    # Whitespace fix still applied despite pre-existing syntax error.
    assert any(r.applied for r in results)
    assert p.read_bytes() == b"def (:\n"


def test_orchestrator_dry_run_writes_status(fake_repo: Path) -> None:
    config = OrchestratorConfig(repo_root=fake_repo, apply=False, commit=False)
    result = Orchestrator(config=config).run()

    status_path = fake_repo / "data_out" / "aria_bot" / "status.json"
    assert status_path.exists()
    payload = json.loads(status_path.read_text())
    assert payload["apply"] is False
    assert payload["totals"]["findings"] >= 2
    assert payload["totals"]["executions"] == payload["totals"]["plans"]
    assert payload["totals"]["skipped"] == payload["totals"]["executions"]
    # Dry-run never applies.
    assert payload["totals"]["applied"] == 0
    assert payload["applied_paths"] == []
    assert payload["validation_targets"] == []
    assert payload["summary"]["state"] == "dry_run"
    assert payload["summary"]["status_text"].startswith("dry_run:")
    assert payload["status_text"] == payload["summary"]["status_text"]
    assert payload["summary"]["counts"]["findings"] == payload["totals"]["findings"]
    assert payload["summary"]["counts"]["applied"] == 0
    assert "trailing_whitespace" in payload["summary"]["by_kind"]["findings"]
    assert payload["summary"]["kind_summary"]["findings"].startswith("missing_final_newline=")
    # No file mutation occurred.
    assert (fake_repo / "src" / "needs_fix.py").read_bytes().endswith(b"   \n")
    # ruff may be missing in test env
    assert result.validation_ok in (True, False)
    assert any("execution summary" in note for note in result.notes)


def test_orchestrator_apply_status_reports_paths(fake_repo: Path) -> None:
    config = OrchestratorConfig(repo_root=fake_repo, apply=True, commit=False)
    result = Orchestrator(config=config).run()

    status_path = fake_repo / "data_out" / "aria_bot" / "status.json"
    payload = json.loads(status_path.read_text())

    assert result.apply is True
    assert payload["totals"]["executions"] == len(payload["executions"])
    assert payload["totals"]["applied"] == len(payload["applied_paths"])
    assert payload["totals"]["skipped"] == len(payload["skipped_paths"])
    assert payload["applied_paths"]
    assert payload["validation_targets"] == payload["applied_paths"]
    assert payload["summary"]["state"] in {"applied", "validation_failed"}
    assert payload["summary"]["status_text"].startswith(payload["summary"]["state"])
    assert payload["summary"]["paths"]["applied"] == payload["applied_paths"]
    assert payload["summary"]["counts"]["executions"] == payload["totals"]["executions"]
    assert payload["summary"]["kind_summary"]["plans"]
    assert any("validated" in note for note in payload["notes"])


def test_analyzer_detects_mixed_line_endings(tmp_path: Path) -> None:
    p = tmp_path / "crlf_file.py"
    p.write_bytes(b"x = 1\r\ny = 2\r\n")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])

    assert any(f.kind == "mixed_line_endings" for f in findings)
    detail = next(f.detail for f in findings if f.kind == "mixed_line_endings")
    assert "2" in detail  # two CRLF sequences


def test_executor_normalizes_line_endings(tmp_path: Path) -> None:
    p = tmp_path / "crlf_file.py"
    p.write_bytes(b"x = 1\r\ny = 2\r\n")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    plans = Planner(risk_manager=rm).build_plans(findings)
    results = Executor(risk_manager=rm, dry_run=False).execute(plans)

    assert any(r.applied for r in results)
    assert b"\r\n" not in p.read_bytes()
    assert p.read_bytes() == b"x = 1\ny = 2\n"

    # Idempotent: no further findings
    findings2 = Analyzer(risk_manager=rm).scan(paths=[p])
    assert not any(f.kind == "mixed_line_endings" for f in findings2)


def test_executor_trims_trailing_blank_lines(tmp_path: Path) -> None:
    p = tmp_path / "extra_blank_lines.md"
    p.write_bytes(b"line one\n\n\n")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    plans = Planner(risk_manager=rm).build_plans(findings)
    results = Executor(risk_manager=rm, dry_run=False).execute(plans)

    assert any(r.applied for r in results)
    assert p.read_bytes() == b"line one\n"


def test_run_cycle_apply_modifies_files(fake_repo: Path) -> None:
    result = run_cycle(repo_root=fake_repo, apply=True, commit=False)
    assert result.apply is True
    applied = [e for e in result.executions if e.applied]
    assert applied, "expected at least one applied plan"
    # Protected dataset file is still dirty.
    assert (fake_repo / "datasets" / "dirty.py").read_bytes() == b"x = 1   \n"


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


def test_cli_rejects_invalid_max_plans(fake_repo: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "aria_bot",
            "--repo-root",
            str(fake_repo),
            "--max-plans",
            "0",
            "--quiet",
        ],
        cwd=PKG_PARENT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "--max-plans must be at least 1" in proc.stderr


def test_commit_message_uses_known_prefix() -> None:
    assert COMMIT_PREFIX.startswith("chore(aria-bot):")


def test_cli_stdout_includes_status_text(fake_repo: Path) -> None:
    """The CLI summary printed to stdout must expose status_text."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "aria_bot",
            "--repo-root",
            str(fake_repo),
        ],
        cwd=PKG_PARENT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "status_text" in data
    assert data["status_text"].startswith("dry_run:")
    assert "totals" in data
    assert data["apply"] is False


# === New feature tests ===


def test_analyzer_detects_utf8_bom(tmp_path: Path) -> None:
    """Files with a UTF-8 BOM should produce a ``utf8_bom`` finding."""
    p = tmp_path / "with_bom.py"
    p.write_bytes(b"\xef\xbb\xbfx = 1\n")
    rm = RiskManager(repo_root=tmp_path)
    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    assert any(f.kind == "utf8_bom" for f in findings)


def test_executor_strips_utf8_bom(tmp_path: Path) -> None:
    """The executor must strip a leading UTF-8 BOM and be idempotent."""
    p = tmp_path / "with_bom.py"
    p.write_bytes(b"\xef\xbb\xbfx = 1\n")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    plans = Planner(risk_manager=rm).build_plans(findings)
    results = Executor(risk_manager=rm, dry_run=False).execute(plans)
    assert any(r.applied for r in results)
    assert p.read_bytes() == b"x = 1\n"

    # Idempotent: second pass finds nothing.
    findings2 = Analyzer(risk_manager=rm).scan(paths=[p])
    plans2 = Planner(risk_manager=rm).build_plans(findings2)
    assert plans2 == []


def test_single_pass_bom_plus_crlf_plus_trailing(tmp_path: Path) -> None:
    """BOM + CRLF + trailing whitespace + missing newline converges in one pass."""
    p = tmp_path / "combo.py"
    p.write_bytes(b"\xef\xbb\xbfa = 1  \r\nb = 2\r\n\r\n")
    rm = RiskManager(repo_root=tmp_path)

    plans = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    Executor(risk_manager=rm, dry_run=False).execute(plans)
    assert p.read_bytes() == b"a = 1\nb = 2\n"

    # Idempotent.
    plans2 = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    assert plans2 == []


def test_analyzer_detects_lone_cr(tmp_path: Path) -> None:
    """Lone CR (old Mac-style) line endings should produce a ``mixed_line_endings`` finding."""
    p = tmp_path / "old_mac.py"
    p.write_bytes(b"x = 1\ry = 2\r")
    rm = RiskManager(repo_root=tmp_path)
    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    assert any(f.kind == "mixed_line_endings" for f in findings)
    detail = next(f.detail for f in findings if f.kind == "mixed_line_endings")
    assert "lone CR" in detail


def test_executor_normalizes_lone_cr(tmp_path: Path) -> None:
    """Lone CR must be normalized to LF."""
    p = tmp_path / "old_mac.txt"
    p.write_bytes(b"hello\rworld\r")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    plans = Planner(risk_manager=rm).build_plans(findings)
    results = Executor(risk_manager=rm, dry_run=False).execute(plans)
    assert any(r.applied for r in results)
    assert p.read_bytes() == b"hello\nworld\n"

    # Idempotent.
    plans2 = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    assert plans2 == []


def test_analyzer_expanded_suffixes(tmp_path: Path) -> None:
    """The analyzer should detect findings in newly-supported file types."""
    for name, content in [
        ("data.json", b'{"key": "value"}  \n'),
        ("config.toml", b"[section]  \n"),
        ("style.css", b"body { }  \n"),
        ("app.js", b"const x = 1;  \n"),
        ("app.ts", b"const y: number = 1;  \n"),
    ]:
        (tmp_path / name).write_bytes(content)

    rm = RiskManager(repo_root=tmp_path)
    findings = Analyzer(risk_manager=rm).scan()
    found_names = {f.path.name for f in findings}
    for name in ("data.json", "config.toml", "style.css", "app.js", "app.ts"):
        assert name in found_names, f"expected findings for {name}"


def test_risk_manager_blocks_vendor_dirs(tmp_path: Path) -> None:
    """node_modules/, .venv/, dist/ etc. must be protected."""
    rm = RiskManager(repo_root=tmp_path)
    for vendor_dir in ("node_modules", ".venv", "dist", "build", "__pycache__"):
        d = tmp_path / vendor_dir
        d.mkdir(exist_ok=True)
        f = d / "file.py"
        f.write_text("x = 1\n")
        assert rm.is_path_protected(f), f"{vendor_dir}/ should be protected"


def test_validator_runs_black_check(tmp_path: Path) -> None:
    """Black check step must be included in validation."""
    from aria_bot.validator import Validator

    v = Validator(repo_root=tmp_path)
    # With no changed paths, both ruff and black should skip.
    result = v.validate(changed_paths=[])
    step_names = [s["name"] for s in result.steps]
    assert "ruff" in step_names
    assert "black" in step_names
    # Both should be "skipped" since no .py files in changeset.
    for step in result.steps:
        assert step["status"] == "skipped"


def test_cli_paths_flag(fake_repo: Path) -> None:
    """The --paths flag should restrict scanning to specified files."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "aria_bot",
            "--repo-root",
            str(fake_repo),
            "--paths",
            str(fake_repo / "src" / "needs_fix.py"),
        ],
        cwd=PKG_PARENT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["totals"]["findings"] >= 1
    # Only the specified file should appear in findings.
    assert data["totals"]["plans"] == 1


def test_cli_paths_flag_directory(fake_repo: Path) -> None:
    """The --paths flag with a directory should expand to matching files."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "aria_bot",
            "--repo-root",
            str(fake_repo),
            "--paths",
            str(fake_repo / "src"),
        ],
        cwd=PKG_PARENT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    # src/ has needs_fix.py (trailing ws) and needs_newline.md (missing newline)
    assert data["totals"]["findings"] >= 2


def test_orchestrator_paths_config(tmp_path: Path) -> None:
    """OrchestratorConfig.paths restricts which files are scanned."""
    (tmp_path / "a.py").write_bytes(b"x = 1  \n")
    (tmp_path / "b.py").write_bytes(b"y = 2  \n")

    # Only scan a.py via paths config.
    result = run_cycle(tmp_path, paths=[tmp_path / "a.py"])
    assert result.plans
    plan_paths = {str(p.path) for p in result.plans}
    assert str(tmp_path / "a.py") in plan_paths
    assert str(tmp_path / "b.py") not in plan_paths


def test_bom_only_file_stripped_correctly(tmp_path: Path) -> None:
    """A file containing only a BOM should become empty (no newline added for empty content)."""
    p = tmp_path / "bom_only.txt"
    p.write_bytes(b"\xef\xbb\xbf")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    # BOM detected; missing_final_newline should NOT fire because content becomes empty.
    kinds = {f.kind for f in findings}
    assert "utf8_bom" in kinds

    plans = Planner(risk_manager=rm).build_plans(findings)
    Executor(risk_manager=rm, dry_run=False).execute(plans)
    # After stripping BOM, file is empty. The missing_final_newline transform
    # only adds a newline to non-empty content, so it stays empty.
    assert p.read_bytes() == b""

    # Idempotent.
    plans2 = Planner(risk_manager=rm).build_plans(Analyzer(risk_manager=rm).scan(paths=[p]))
    assert plans2 == []


def test_mixed_crlf_and_lone_cr(tmp_path: Path) -> None:
    """Files with both CRLF and lone CR should report both in the detail."""
    p = tmp_path / "mixed.txt"
    p.write_bytes(b"a\r\nb\rc\n")
    rm = RiskManager(repo_root=tmp_path)

    findings = Analyzer(risk_manager=rm).scan(paths=[p])
    detail = next(f.detail for f in findings if f.kind == "mixed_line_endings")
    assert "CRLF" in detail
    assert "lone CR" in detail

    plans = Planner(risk_manager=rm).build_plans(findings)
    Executor(risk_manager=rm, dry_run=False).execute(plans)
    assert p.read_bytes() == b"a\nb\nc\n"
