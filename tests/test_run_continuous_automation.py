"""Unit tests for run_continuous_automation.py.

Covers the platform marker helper and the ContinuousAutomationDaemon's
deterministic logic (initialization, logging, automation cycle outcomes, and
next-run formatting) using mocked subprocess calls.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


def _load_module():
    script_path = Path(__file__).parent.parent / "run_continuous_automation.py"
    spec = importlib.util.spec_from_file_location("run_continuous_automation", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# get_marker
# ---------------------------------------------------------------------------


def test_get_marker_unix(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod.sys, "platform", "linux")

    assert mod.get_marker("ok") == "✓"
    assert mod.get_marker("error") == "✗"


def test_get_marker_windows(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod.sys, "platform", "win32")

    assert mod.get_marker("ok") == "[OK]"
    assert mod.get_marker("warning") == "[WARN]"


def test_get_marker_unknown_key_returns_fallback():
    mod = _load_module()
    assert mod.get_marker("does-not-exist") == "[*]"


# ---------------------------------------------------------------------------
# ContinuousAutomationDaemon
# ---------------------------------------------------------------------------


def _make_daemon(mod, tmp_path, interval_minutes=60):
    return mod.ContinuousAutomationDaemon(tmp_path, interval_minutes=interval_minutes)


def test_daemon_init_sets_fields_and_creates_logs_dir(tmp_path):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path, interval_minutes=15)

    assert daemon.workspace_root == tmp_path
    assert daemon.interval_minutes == 15
    assert daemon.interval_seconds == 15 * 60
    assert daemon.run_count == 0
    assert daemon.running is True
    assert daemon.automation_script == tmp_path / "run_automation.py"
    assert daemon.log_file.parent.exists()


def test_log_message_appends_timestamped_line(tmp_path):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path)

    daemon.log_message("hello world")
    daemon.log_message("second line")

    contents = daemon.log_file.read_text(encoding="utf-8")
    lines = [line for line in contents.splitlines() if line]
    assert len(lines) == 2
    assert lines[0].startswith("[") and "] hello world" in lines[0]
    assert "second line" in lines[1]


def test_run_automation_success_increments_count(tmp_path, monkeypatch):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path)

    calls = {}

    def fake_run(cmd, *args, **kwargs):
        calls["cmd"] = cmd
        calls["kwargs"] = kwargs
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    assert daemon.run_automation() is True
    assert daemon.run_count == 1

    # Verify the subprocess call contract, not just the return handling.
    assert str(daemon.automation_script) in calls["cmd"]
    assert calls["kwargs"]["cwd"] == str(tmp_path)
    assert calls["kwargs"]["timeout"] == 600
    assert calls["kwargs"]["capture_output"] is True
    assert calls["kwargs"]["text"] is True


def test_run_automation_nonzero_returncode_still_true(tmp_path, monkeypatch):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], returncode=2, stdout="some output", stderr="warn")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    # Failures must not stop the daemon; cycle reports True.
    assert daemon.run_automation() is True
    assert daemon.run_count == 1


def test_run_automation_timeout_returns_false(tmp_path, monkeypatch):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path)

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=600)

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    assert daemon.run_automation() is False


def test_run_automation_generic_exception_returns_false(tmp_path, monkeypatch):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path)

    def fake_run(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    assert daemon.run_automation() is False


def test_calculate_next_run_returns_formatted_timestamp(tmp_path):
    mod = _load_module()
    daemon = _make_daemon(mod, tmp_path, interval_minutes=30)

    import datetime as _dt

    before = _dt.datetime.now()
    result = daemon.calculate_next_run()
    after = _dt.datetime.now()

    # Format is "%Y-%m-%d %H:%M:%S" and the value reflects now + interval.
    parsed = _dt.datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
    expected_low = before + _dt.timedelta(seconds=daemon.interval_seconds)
    expected_high = after + _dt.timedelta(seconds=daemon.interval_seconds)
    # Allow a 2s tolerance for second-level truncation in strftime.
    assert expected_low - _dt.timedelta(seconds=2) <= parsed
    assert parsed <= expected_high + _dt.timedelta(seconds=2)
