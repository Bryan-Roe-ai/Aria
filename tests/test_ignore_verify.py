from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

pytestmark = pytest.mark.unit


def _ignore_verify() -> Any:
    import scripts.ignore_verify as ignore_verify

    return ignore_verify


def test_main_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    mod = _ignore_verify()
    (tmp_path / ".gitignore").write_text(
        "**/.venv/\n**/venv/\n",
        encoding="utf-8",
    )

    class _Result:
        returncode = 0

    def _fake_run(*args: Any, **kwargs: Any) -> _Result:
        return _Result()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod.subprocess, "run", _fake_run)

    assert mod.main() == 0


def test_main_fails_when_patterns_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    mod = _ignore_verify()
    (tmp_path / ".gitignore").write_text(
        "# missing recursive patterns\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert mod.main() == 1


def test_main_fails_when_git_check_ignore_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    mod = _ignore_verify()
    (tmp_path / ".gitignore").write_text(
        "**/.venv/\n**/venv/\n",
        encoding="utf-8",
    )

    class _Result:
        returncode = 1

    def _fake_run(*args: Any, **kwargs: Any) -> _Result:
        return _Result()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod.subprocess, "run", _fake_run)

    assert mod.main() == 1
