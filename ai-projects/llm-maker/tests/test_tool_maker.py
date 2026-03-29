"""Tests for ToolMaker provider initialization and generation behavior."""

import sys
from pathlib import Path

import pytest
import yaml

# Add repo root and src to path
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import tool_maker
from tool_maker import ToolMaker


class _FakeProvider:
    def __init__(self, chunks=None):
        self._chunks = chunks or []

    def complete(self, messages, stream=True):
        if stream:
            for chunk in self._chunks:
                yield chunk
        else:
            return "".join(self._chunks)


@pytest.mark.parametrize("provider_name", ["auto", "lmstudio", "local"])
def test_initialize_provider_accepts_detect_provider_tuple(monkeypatch, tmp_path, provider_name):
    """ToolMaker should accept detect_provider() tuple returns and keep provider object."""
    fake_provider = _FakeProvider()

    def fake_detect_provider(explicit):
        return fake_provider, {"name": explicit}

    monkeypatch.setattr(tool_maker, "detect_provider", fake_detect_provider)

    cfg = {
        "tool_maker": {
            "provider": provider_name,
            "temperature": 0.2,
            "max_tokens": 256,
        }
    }
    cfg_path = tmp_path / "llm_maker_test.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    maker = ToolMaker(config_path=cfg_path)

    assert maker.provider is fake_provider


def test_initialize_provider_fallback_handles_tuple(monkeypatch, tmp_path):
    """When first provider detection is falsy, local fallback tuple should be unpacked."""
    fallback_provider = _FakeProvider()

    calls = []

    def fake_detect_provider(explicit):
        calls.append(explicit)
        if explicit == "auto":
            return None, {"name": "none"}
        if explicit == "local":
            return fallback_provider, {"name": "local"}
        return None, {"name": explicit}

    monkeypatch.setattr(tool_maker, "detect_provider", fake_detect_provider)

    cfg = {
        "tool_maker": {
            "provider": "auto",
            "temperature": 0.2,
            "max_tokens": 256,
        }
    }
    cfg_path = tmp_path / "llm_maker_test.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    maker = ToolMaker(config_path=cfg_path)

    assert maker.provider is fallback_provider
    assert calls == ["auto", "local"]


def test_generate_code_uses_unpacked_provider(monkeypatch, tmp_path):
    """Generated code path should call .complete on provider object, not a tuple."""
    fake_code = "def sample(a: int) -> int:\n    return a + 1"
    fake_provider = _FakeProvider(chunks=[fake_code])

    def fake_detect_provider(explicit):
        return fake_provider, {"name": explicit}

    monkeypatch.setattr(tool_maker, "detect_provider", fake_detect_provider)

    cfg = {
        "tool_maker": {
            "provider": "auto",
            "temperature": 0.2,
            "max_tokens": 256,
        }
    }
    cfg_path = tmp_path / "llm_maker_test.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    maker = ToolMaker(config_path=cfg_path)
    code = maker._generate_code("Generate function")

    assert code is not None
    assert code.strip().startswith("def sample")
