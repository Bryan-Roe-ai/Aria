"""
Unit tests for CircuitCache and QuantumLLMPipeline gaps not in test_quantum_llm.py.

Covers:
- CircuitCache LRU eviction, TTL expiry, stats, invalid inputs
- QuantumSampler.cache_stats() (cache enabled vs disabled)
- QuantumLLMPipeline.stream() with empty / whitespace-only prompt
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import numpy as np
import pytest

_QUANTUM_LLM_SRC = Path(__file__).resolve().parents[1] / "ai-projects" / "quantum-ml" / "src"
if str(_QUANTUM_LLM_SRC) not in sys.path:
    sys.path.insert(0, str(_QUANTUM_LLM_SRC))

from quantum_llm import CircuitCache, QuantumLLMConfig, QuantumLLMPipeline, QuantumSampler  # noqa: E402


# ===========================================================================
# Helpers
# ===========================================================================


class _MockProvider:
    def __init__(self, text: str = "mock response"):
        self.name = "mock"
        self._text = text

    def complete(self, messages, stream=False):
        if stream:
            return iter(self._text.split())
        return self._text


def _make_params(n: int = 8, seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).random(n)


# ===========================================================================
# CircuitCache — basic operations
# ===========================================================================


class TestCircuitCacheBasic:
    def test_put_and_get_roundtrip(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        params = _make_params()
        probs = np.array([0.25, 0.25, 0.25, 0.25])
        cache.put(params, 4, probs)
        result = cache.get(params, 4)
        assert result is not None
        np.testing.assert_array_almost_equal(result, probs)

    def test_get_missing_returns_none(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        assert cache.get(_make_params(), 4) is None

    def test_different_qubits_are_separate_keys(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        params = _make_params()
        probs4 = np.array([0.1, 0.2, 0.3, 0.4])
        probs2 = np.array([0.6, 0.4])
        cache.put(params, 4, probs4)
        cache.put(params, 2, probs2)
        np.testing.assert_array_almost_equal(cache.get(params, 4), probs4)
        np.testing.assert_array_almost_equal(cache.get(params, 2), probs2)

    def test_put_returns_copy_not_reference(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        params = _make_params()
        probs = np.array([0.5, 0.5])
        cache.put(params, 2, probs)
        probs[:] = 0.0  # mutate original
        result = cache.get(params, 2)
        assert result is not None
        assert not np.allclose(result, 0.0), "cache must store a copy, not a reference"

    def test_clear_empties_cache(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        params = _make_params()
        cache.put(params, 4, np.ones(4) / 4)
        cache.clear()
        assert cache.get(params, 4) is None
        assert cache.stats()["size"] == 0


# ===========================================================================
# CircuitCache — LRU eviction
# ===========================================================================


class TestCircuitCacheLRU:
    def test_lru_evicts_oldest_on_overflow(self):
        cache = CircuitCache(max_size=3, max_age_seconds=0)  # TTL=0 means no expiry
        rng = np.random.default_rng(7)
        all_params = [rng.random(4) for _ in range(4)]
        probs = np.array([0.25, 0.25, 0.25, 0.25])

        # Fill to capacity with entries A, B, C
        cache.put(all_params[0], 4, probs)
        cache.put(all_params[1], 4, probs)
        cache.put(all_params[2], 4, probs)

        # Insert D — should evict A (oldest)
        cache.put(all_params[3], 4, probs)

        assert cache.get(all_params[0], 4) is None, "Oldest entry should have been evicted"
        assert cache.get(all_params[1], 4) is not None
        assert cache.get(all_params[2], 4) is not None
        assert cache.get(all_params[3], 4) is not None

    def test_lru_access_refreshes_entry(self):
        """Accessing an entry before overflow should protect it from eviction."""
        cache = CircuitCache(max_size=3, max_age_seconds=0)
        rng = np.random.default_rng(8)
        params = [rng.random(4) for _ in range(4)]
        probs = np.array([0.25, 0.25, 0.25, 0.25])

        cache.put(params[0], 4, probs)
        cache.put(params[1], 4, probs)
        cache.put(params[2], 4, probs)

        # Touch params[0] — it becomes most recently used
        cache.get(params[0], 4)

        # Overflow: params[1] should now be evicted (it's the least recently used)
        cache.put(params[3], 4, probs)

        assert cache.get(params[0], 4) is not None, "Accessed entry should survive eviction"
        assert cache.get(params[1], 4) is None, "Least-recently-used entry should be evicted"

    def test_eviction_counter_increments(self):
        cache = CircuitCache(max_size=2, max_age_seconds=0)
        rng = np.random.default_rng(9)
        for i in range(5):
            cache.put(rng.random(4), 4, np.ones(4) / 4)
        assert cache.stats()["evictions"] >= 3


# ===========================================================================
# CircuitCache — TTL expiry
# ===========================================================================


class TestCircuitCacheTTL:
    def test_expired_entry_returns_none(self):
        cache = CircuitCache(max_size=10, max_age_seconds=0.05)
        params = _make_params()
        cache.put(params, 4, np.ones(4) / 4)
        time.sleep(0.1)  # exceed TTL
        assert cache.get(params, 4) is None

    def test_non_expired_entry_is_valid(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        params = _make_params()
        cache.put(params, 4, np.ones(4) / 4)
        assert cache.get(params, 4) is not None

    def test_zero_ttl_means_no_expiry(self):
        """max_age_seconds=0 is treated as 'never expire'."""
        cache = CircuitCache(max_size=10, max_age_seconds=0)
        params = _make_params()
        cache.put(params, 4, np.ones(4) / 4)
        time.sleep(0.05)
        assert cache.get(params, 4) is not None

    def test_expiration_counter_increments(self):
        cache = CircuitCache(max_size=10, max_age_seconds=0.05)
        params = _make_params()
        cache.put(params, 4, np.ones(4) / 4)
        time.sleep(0.1)
        cache.get(params, 4)  # triggers expiration
        assert cache.stats()["expirations"] >= 1


# ===========================================================================
# CircuitCache — stats
# ===========================================================================


class TestCircuitCacheStats:
    def test_initial_stats_are_zero(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        s = cache.stats()
        assert s["size"] == 0
        assert s["hits"] == 0
        assert s["misses"] == 0
        assert s["hit_rate"] == 0.0
        assert s["evictions"] == 0

    def test_hit_and_miss_counts(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        params = _make_params()
        cache.get(params, 4)  # miss
        cache.put(params, 4, np.ones(4) / 4)
        cache.get(params, 4)  # hit
        s = cache.stats()
        assert s["hits"] == 1
        assert s["misses"] == 1
        assert s["hit_rate"] == pytest.approx(0.5)

    def test_size_reflects_stored_entries(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        rng = np.random.default_rng(3)
        for _ in range(5):
            cache.put(rng.random(4), 4, np.ones(4) / 4)
        assert cache.stats()["size"] == 5
        assert cache.stats()["max_size"] == 10


# ===========================================================================
# CircuitCache — invalid inputs
# ===========================================================================


class TestCircuitCacheInvalidInputs:
    def test_get_with_non_numeric_params_returns_none(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        assert cache.get(["not", "numbers"], 4) is None  # type: ignore[arg-type]

    def test_put_with_non_numeric_params_is_ignored(self):
        """put() with invalid params should silently no-op."""
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        cache.put(["bad"], 4, np.ones(4) / 4)  # type: ignore[arg-type]
        assert cache.stats()["size"] == 0

    def test_put_with_empty_probs_is_ignored(self):
        cache = CircuitCache(max_size=10, max_age_seconds=60)
        cache.put(_make_params(), 4, np.array([]))
        assert cache.stats()["size"] == 0

    def test_max_size_clamped_to_one(self):
        """max_size=0 or negative is silently clamped to 1."""
        cache = CircuitCache(max_size=0, max_age_seconds=60)
        assert cache.max_size == 1


# ===========================================================================
# QuantumSampler — cache_stats
# ===========================================================================


class TestQuantumSamplerCacheStats:
    def test_cache_enabled_returns_stats_dict(self):
        s = QuantumSampler(backend="classical", num_qubits=4, shots=128, cache_enabled=True)
        stats = s.cache_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_cache_disabled_returns_empty_dict(self):
        s = QuantumSampler(backend="classical", num_qubits=4, shots=128, cache_enabled=False)
        assert s.cache_stats() == {}

    def test_cache_hit_after_repeated_sample(self):
        """Identical params on consecutive calls should register cache hits."""
        s = QuantumSampler(backend="classical", num_qubits=4, shots=128, seed=0, cache_enabled=True)
        logits = [1.0, 2.0, 0.5, 0.1]
        s.sample(logits, blend_factor=0.3, seed=1)
        s.sample(logits, blend_factor=0.3, seed=2)  # same params → cache hit
        assert s.cache_stats()["hits"] >= 1


# ===========================================================================
# QuantumLLMPipeline — empty / whitespace prompt in stream()
# ===========================================================================


class TestPipelineStreamEmptyPrompt:
    def _make_pipeline(self) -> QuantumLLMPipeline:
        cfg = QuantumLLMConfig(backend="classical", use_thread=False)
        pipeline = QuantumLLMPipeline(config=cfg)
        pipeline._get_provider = lambda prompt, provider=None: _MockProvider("hello")
        return pipeline

    def test_stream_empty_string_yields_done(self):
        pipeline = self._make_pipeline()

        async def collect():
            return [chunk async for chunk in pipeline.stream("")]

        chunks = asyncio.run(collect())
        assert any("[DONE]" in c for c in chunks)

    def test_stream_whitespace_only_yields_done(self):
        pipeline = self._make_pipeline()

        async def collect():
            return [chunk async for chunk in pipeline.stream("   \t\n  ")]

        chunks = asyncio.run(collect())
        assert any("[DONE]" in c for c in chunks)

    def test_stream_empty_prompt_no_meta_event(self):
        """Empty prompt short-circuit must not emit the meta event (no provider call)."""
        pipeline = self._make_pipeline()

        async def collect():
            return [chunk async for chunk in pipeline.stream("")]

        chunks = asyncio.run(collect())
        assert not any("event: meta" in c for c in chunks)

    def test_stream_empty_prompt_quantum_augmented_false(self):
        """Short-circuit response must report quantum_augmented=False."""
        import json

        pipeline = self._make_pipeline()

        async def collect():
            return [chunk async for chunk in pipeline.stream("")]

        chunks = asyncio.run(collect())
        data_chunks = [c for c in chunks if c.startswith("data:") and "[DONE]" not in c]
        found = False
        for chunk in data_chunks:
            payload = json.loads(chunk.split("data:", 1)[1].strip())
            if "quantum_augmented" in payload:
                assert payload["quantum_augmented"] is False
                found = True
        assert found, "Expected a chunk with quantum_augmented=False"

    def test_stream_normal_prompt_still_works(self):
        """Confirm non-empty prompts still flow through the full pipeline."""
        pipeline = self._make_pipeline()

        async def collect():
            return [chunk async for chunk in pipeline.stream("What is quantum?")]

        chunks = asyncio.run(collect())
        assert any("[DONE]" in c for c in chunks)
        assert any("event: meta" in c for c in chunks), "Meta event expected for non-empty prompt"
