"""Tests for the provider-detection cache layer in chat_providers.py."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_CHAT_SRC = Path(__file__).resolve().parents[1] / "ai-projects" / "chat-cli" / "src"
if str(_CHAT_SRC) not in sys.path:
    sys.path.insert(0, str(_CHAT_SRC))

import chat_providers as cp


def _clear_cache() -> None:
    with cp._provider_detection_cache_lock:
        cp._provider_detection_cache.clear()


def _make_fake_provider(name: str = "local") -> cp.BaseChatProvider:
    mock = MagicMock(spec=cp.BaseChatProvider)
    mock.name = name
    return mock


def _make_choice(name: str = "local", model: str = "m") -> cp.ProviderChoice:
    return cp.ProviderChoice(name=name, model=model)


class TestGetCacheTTL:
    def test_returns_default_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("QAI_PROVIDER_DETECT_CACHE_TTL", raising=False)
        ttl = cp._get_provider_detect_cache_ttl_seconds()
        assert ttl == cp._PROVIDER_DETECT_CACHE_TTL_SECONDS

    def test_env_overrides_default(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "42.5")
        ttl = cp._get_provider_detect_cache_ttl_seconds()
        assert ttl == 42.5

    def test_respects_minimum_bound(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "-10")
        ttl = cp._get_provider_detect_cache_ttl_seconds()
        assert ttl == 0.0

    def test_respects_maximum_bound(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "99999")
        ttl = cp._get_provider_detect_cache_ttl_seconds()
        assert ttl == 300.0


class TestCacheSetGet:
    def setup_method(self):
        _clear_cache()

    def test_set_and_get_round_trip(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        provider = _make_fake_provider("local")
        choice = _make_choice("local", "test-model")
        key = ("local", None, None, None)
        cp._set_cached_provider_detection(key, provider, choice)
        result = cp._get_cached_provider_detection(key)
        assert result is not None
        got_provider, got_choice = result
        assert got_provider is provider
        assert got_choice is choice

    def test_cache_miss_returns_none_for_unknown_key(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        result = cp._get_cached_provider_detection(("nonexistent", None, None, None))
        assert result is None

    def test_ttl_zero_disables_set(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "0")
        key = ("local", None, None, None)
        cp._set_cached_provider_detection(key, _make_fake_provider(), _make_choice())
        with cp._provider_detection_cache_lock:
            assert key not in cp._provider_detection_cache

    def test_ttl_zero_disables_get(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "0")
        key = ("local", None, None, None)
        with cp._provider_detection_cache_lock:
            cp._provider_detection_cache[key] = {
                "provider": _make_fake_provider(), "choice": _make_choice(),
                "cached_at": time.time(),
            }
        assert cp._get_cached_provider_detection(key) is None

    def test_expired_entry_returns_none(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "0.001")
        key = ("local", None, None, None)
        with cp._provider_detection_cache_lock:
            cp._provider_detection_cache[key] = {
                "provider": _make_fake_provider(), "choice": _make_choice(),
                "cached_at": time.time() - 1.0,
            }
        assert cp._get_cached_provider_detection(key) is None

    def test_expired_entry_removed_from_dict(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "0.001")
        key = ("local", None, None, None)
        with cp._provider_detection_cache_lock:
            cp._provider_detection_cache[key] = {
                "provider": _make_fake_provider(), "choice": _make_choice(),
                "cached_at": time.time() - 1.0,
            }
        cp._get_cached_provider_detection(key)
        with cp._provider_detection_cache_lock:
            assert key not in cp._provider_detection_cache

    def test_different_keys_dont_cross_contaminate(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        p1, c1 = _make_fake_provider("a"), _make_choice("a")
        p2, c2 = _make_fake_provider("b"), _make_choice("b")
        k1, k2 = ("k1", None, None, None), ("k2", None, None, None)
        cp._set_cached_provider_detection(k1, p1, c1)
        cp._set_cached_provider_detection(k2, p2, c2)
        r1 = cp._get_cached_provider_detection(k1)
        r2 = cp._get_cached_provider_detection(k2)
        assert r1 is not None and r1[0] is p1
        assert r2 is not None and r2[0] is p2

    def test_corrupt_entry_missing_provider_returns_none(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        key = ("local", None, None, None)
        with cp._provider_detection_cache_lock:
            cp._provider_detection_cache[key] = {
                "provider": None, "choice": _make_choice(), "cached_at": time.time(),
            }
        assert cp._get_cached_provider_detection(key) is None

    def test_corrupt_entry_missing_choice_returns_none(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        key = ("local", None, None, None)
        with cp._provider_detection_cache_lock:
            cp._provider_detection_cache[key] = {
                "provider": _make_fake_provider(), "choice": None, "cached_at": time.time(),
            }
        assert cp._get_cached_provider_detection(key) is None


class TestCacheProviderResult:
    def setup_method(self):
        _clear_cache()

    def test_returns_provider_and_choice_unchanged(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        p, c = _make_fake_provider(), _make_choice()
        rp, rc = cp._cache_provider_result(("k", None, None, None), p, c)
        assert rp is p and rc is c

    def test_caches_into_backing_dict(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        key = ("local2", None, None, None)
        cp._cache_provider_result(key, _make_fake_provider(), _make_choice())
        with cp._provider_detection_cache_lock:
            assert key in cp._provider_detection_cache

    def test_none_key_skips_caching(self, monkeypatch):
        monkeypatch.setenv("QAI_PROVIDER_DETECT_CACHE_TTL", "60")
        before = len(cp._provider_detection_cache)
        cp._cache_provider_result(None, _make_fake_provider(), _make_choice())
        assert len(cp._provider_detection_cache) == before


class TestBuildCacheKey:
    def test_returns_tuple(self, monkeypatch):
        monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)
        key = cp._build_provider_detect_cache_key("local", None, None, None)
        assert isinstance(key, tuple) and len(key) > 4

    def test_different_provider_choice_different_key(self, monkeypatch):
        monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)
        k1 = cp._build_provider_detect_cache_key("local", None, None, None)
        k2 = cp._build_provider_detect_cache_key("openai", None, None, None)
        assert k1 != k2

    def test_env_change_changes_key(self, monkeypatch):
        monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
        k1 = cp._build_provider_detect_cache_key("auto", None, None, None)
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
        k2 = cp._build_provider_detect_cache_key("auto", None, None, None)
        assert k1 != k2

    def test_model_override_changes_key(self, monkeypatch):
        monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)
        k1 = cp._build_provider_detect_cache_key("local", None, None, None)
        k2 = cp._build_provider_detect_cache_key("local", "gpt-4o", None, None)
        assert k1 != k2
