"""
Regression tests for QuantumSampler handling of non-finite logits.
"""

from __future__ import annotations

import sys
from pathlib import Path

_QUANTUM_LLM_SRC = Path(__file__).resolve().parents[1] / "ai-projects" / "quantum-ml" / "src"
if str(_QUANTUM_LLM_SRC) not in sys.path:
    sys.path.insert(0, str(_QUANTUM_LLM_SRC))

from quantum_llm import QuantumSampler  # noqa: E402


def _make_sampler() -> QuantumSampler:
    return QuantumSampler(backend="classical", num_qubits=2, shots=64, num_layers=1, seed=0)


def test_sample_replaces_nan_logits():
    idx = _make_sampler().sample([float("nan"), 1.0, 0.5], blend_factor=0.3, seed=1)
    assert 0 <= idx < 3


def test_sample_replaces_positive_infinity_logits():
    idx = _make_sampler().sample([float("inf"), 1.0, 0.5], blend_factor=0.3, seed=1)
    assert 0 <= idx < 3


def test_sample_replaces_all_negative_infinity_logits():
    idx = _make_sampler().sample([float("-inf"), float("-inf"), float("-inf")], blend_factor=0.3, seed=1)
    assert 0 <= idx < 3
