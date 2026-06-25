"""
Regression tests for non-streaming quantum provider result normalization.

Ensures bytes-oriented provider payloads decode into text instead of joining
their integer byte values.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_QUANTUM_LLM_SRC = Path(__file__).resolve().parents[1] / "ai-projects" / "quantum-ml" / "src"
if str(_QUANTUM_LLM_SRC) not in sys.path:
    sys.path.insert(0, str(_QUANTUM_LLM_SRC))

from quantum_llm import QuantumLLMConfig, QuantumLLMPipeline  # noqa: E402


class _BytesProvider:
    name = "bytes-provider"

    def complete(self, messages, stream=False):
        return b"hi"


class _BytearrayProvider:
    name = "bytearray-provider"

    def complete(self, messages, stream=False):
        return bytearray(b"hi")


class _ChunkedBytesProvider:
    name = "chunked-bytes-provider"

    def complete(self, messages, stream=False):
        return [b"he", bytearray(b"ll"), "o"]


def _make_pipeline(provider):
    pipeline = QuantumLLMPipeline(QuantumLLMConfig(backend="classical", num_qubits=2, shots=64, use_thread=False))
    pipeline._get_provider = lambda prompt, provider_override=None: provider
    return pipeline


def test_generate_decodes_bytes_payload():
    result = asyncio.run(_make_pipeline(_BytesProvider()).generate("bytes payload"))
    assert result["response"] == "hi"


def test_generate_decodes_bytearray_payload():
    result = asyncio.run(_make_pipeline(_BytearrayProvider()).generate("bytearray payload"))
    assert result["response"] == "hi"


def test_generate_decodes_chunked_bytes_payload():
    result = asyncio.run(_make_pipeline(_ChunkedBytesProvider()).generate("chunked payload"))
    assert result["response"] == "hello"
