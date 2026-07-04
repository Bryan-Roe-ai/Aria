"""Unit tests for scripts/lm_studio_analyzer.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "lm_studio_analyzer.py"


@pytest.fixture()
def analyzer_module():
    """Load lm_studio_analyzer as a module from scripts/."""
    spec = importlib.util.spec_from_file_location("lm_studio_analyzer", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_loads_env_defaults_from_dotenv_and_local_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, analyzer_module
) -> None:
    """Analyzer should bootstrap env defaults from local files when unset."""
    (tmp_path / ".env").write_text(
        "LMSTUDIO_BASE_URL=http://host.docker.internal:1234/v1\nLMSTUDIO_MODEL=from-env-file\nLMSTUDIO_TIMEOUT=120\n",
        encoding="utf-8",
    )
    (tmp_path / "local.settings.json").write_text(
        json.dumps(
            {
                "Values": {
                    "LMSTUDIO_BASE_URL": "http://ignored:1234/v1",
                    "LMSTUDIO_MODEL": "from-local-settings",
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("LMSTUDIO_BASE_URL", raising=False)
    monkeypatch.delenv("LMSTUDIO_MODEL", raising=False)

    monkeypatch.setattr(
        analyzer_module.LMStudioAnalyzer,
        "_find_repo_root",
        lambda self: tmp_path,
    )

    analyzer = analyzer_module.LMStudioAnalyzer()

    assert analyzer.base_url == "http://host.docker.internal:1234/v1"
    assert analyzer.model == "from-env-file"


def test_query_invokes_chat_cli_with_no_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, analyzer_module
) -> None:
    """Analyzer query should invoke chat_cli with no-stream and env vars."""
    (tmp_path / "local.settings.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        analyzer_module.LMStudioAnalyzer,
        "_find_repo_root",
        lambda self: tmp_path,
    )

    captured: dict[str, object] = {}

    def fake_run(cmd, **kwargs):  # noqa: ANN001
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs

        class Result:
            returncode = 0
            stdout = "Provider: lmstudio\nassistant> OK\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(analyzer_module.subprocess, "run", fake_run)

    analyzer = analyzer_module.LMStudioAnalyzer(
        base_url="http://host.docker.internal:1234/v1",
        model="local-model",
        timeout=77,
    )
    result = analyzer.query("Reply with OK only")

    assert "assistant> OK" in result
    cmd = captured["cmd"]
    kwargs = captured["kwargs"]
    assert isinstance(cmd, list)
    assert "--no-stream" in cmd
    assert kwargs["timeout"] == 77
    assert kwargs["env"]["LMSTUDIO_BASE_URL"] == "http://host.docker.internal:1234/v1"
    assert kwargs["env"]["LMSTUDIO_MODEL"] == "local-model"


def test_query_timeout_returns_friendly_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, analyzer_module) -> None:
    """Timeouts should map to a user-friendly error string."""
    (tmp_path / "local.settings.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        analyzer_module.LMStudioAnalyzer,
        "_find_repo_root",
        lambda self: tmp_path,
    )

    def fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="chat_cli.py", timeout=5)

    monkeypatch.setattr(analyzer_module.subprocess, "run", fake_run)

    analyzer = analyzer_module.LMStudioAnalyzer()
    result = analyzer.query("hello")

    assert "Query timeout" in result


# ---------------------------------------------------------------------------
# Prompt shape tests for each public method
# ---------------------------------------------------------------------------


@pytest.fixture()
def capturing_analyzer(tmp_path, monkeypatch, analyzer_module):
    """Return an LMStudioAnalyzer whose prompts are captured, not sent."""
    (tmp_path / "local.settings.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        analyzer_module.LMStudioAnalyzer,
        "_find_repo_root",
        lambda self: tmp_path,
    )

    captured: dict[str, str] = {}

    def fake_query(self, prompt, timeout=None):  # noqa: ANN001
        captured["prompt"] = prompt
        return "OK"

    monkeypatch.setattr(analyzer_module.LMStudioAnalyzer, "_query_lmstudio", fake_query)
    analyzer = analyzer_module.LMStudioAnalyzer()
    return analyzer, captured


def test_analyze_code_prompt_contains_language(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.analyze_code("def f(): pass", language="typescript")
    assert "typescript" in captured["prompt"]
    assert "def f(): pass" in captured["prompt"]


def test_generate_docstring_prompt_contains_code(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.generate_docstring("class Foo: pass")
    assert "class Foo: pass" in captured["prompt"]
    assert "docstring" in captured["prompt"].lower() or "documentation" in captured["prompt"].lower()


def test_generate_tests_uses_pytest_for_python(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.generate_tests("def add(a, b): return a + b")
    assert "pytest" in captured["prompt"]


def test_generate_tests_uses_jest_for_js(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.generate_tests("function add(a,b){return a+b}", language="javascript")
    assert "jest" in captured["prompt"]


def test_refactor_code_prompt_contains_code(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.refactor_code("x = 1+1")
    assert "x = 1+1" in captured["prompt"]
    assert "refactor" in captured["prompt"].lower()


def test_debug_error_includes_error_text(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.debug_error("AttributeError: 'NoneType'")
    assert "AttributeError: 'NoneType'" in captured["prompt"]


def test_debug_error_appends_context_when_given(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.debug_error("KeyError: 'model'", context="during provider detection")
    assert "during provider detection" in captured["prompt"]


def test_design_solution_includes_problem(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.design_solution("Need SSE streaming for Aria chat")
    assert "Need SSE streaming for Aria chat" in captured["prompt"]


def test_explain_concept_includes_concept(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.explain_concept("semantic memory")
    assert "semantic memory" in captured["prompt"]


def test_explain_concept_appends_context(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.explain_concept("LoRA", context="fine-tuning quantum models")
    assert "fine-tuning quantum models" in captured["prompt"]


def test_review_code_prompt_covers_security(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.review_code("def get(x): return db.query(x)")
    assert "security" in captured["prompt"].lower()
    assert "def get(x)" in captured["prompt"]


def test_summarize_file_prompt_asks_for_entry_points(capturing_analyzer) -> None:
    analyzer, captured = capturing_analyzer
    analyzer.summarize_file("def main(): pass")
    assert "entry point" in captured["prompt"].lower() or "exports" in captured["prompt"].lower()
    assert "def main(): pass" in captured["prompt"]
