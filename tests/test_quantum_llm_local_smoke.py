"""Regression tests for the safest local Quantum LLM smoke path."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_QUANTUM_LLM_SRC = Path(__file__).resolve().parents[1] / "ai-projects" / "quantum-ml" / "src"
if str(_QUANTUM_LLM_SRC) not in sys.path:
    sys.path.insert(0, str(_QUANTUM_LLM_SRC))

from quantum_llm import QuantumLLMConfig, QuantumLLMPipeline  # noqa: E402


def test_generate_local_provider_bypasses_detect_provider():
    pipeline = QuantumLLMPipeline(
        config=QuantumLLMConfig(
            backend="classical",
            provider="local",
            num_qubits=2,
            shots=64,
            use_thread=False,
        )
    )

    def _unexpected_detect_provider(**_kwargs):
        raise AssertionError("detect_provider should not run for explicit local provider")

    pipeline._detect_provider = _unexpected_detect_provider

    result = asyncio.run(pipeline.generate("Local-only smoke"))

    assert result["provider"] == "local-echo"
    assert result["response"] == "[quantum-llm echo] Local-only smoke"


def test_generate_explicit_local_override_bypasses_detect_provider():
    pipeline = QuantumLLMPipeline(
        config=QuantumLLMConfig(
            backend="classical",
            provider="auto",
            num_qubits=2,
            shots=64,
            use_thread=False,
        )
    )

    def _unexpected_detect_provider(**_kwargs):
        raise AssertionError("detect_provider should not run for provider override 'local'")

    pipeline._detect_provider = _unexpected_detect_provider

    result = asyncio.run(pipeline.generate("Override to local", provider="local"))

    assert result["provider"] == "local-echo"
    assert result["response"] == "[quantum-llm echo] Override to local"
