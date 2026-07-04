"""
Regression tests for quantum LLM streaming error handling.

Ensures the SSE stream terminates cleanly even when a provider raises partway
through iteration.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_QUANTUM_LLM_SRC = Path(__file__).resolve().parents[1] / "ai-projects" / "quantum-ml" / "src"
if str(_QUANTUM_LLM_SRC) not in sys.path:
    sys.path.insert(0, str(_QUANTUM_LLM_SRC))

from quantum_llm import QuantumLLMConfig, QuantumLLMPipeline  # noqa: E402


class _BrokenStreamProvider:
    name = "broken-stream-provider"

    def complete(self, messages, stream=False):
        if not stream:
            return "unused"

        def _chunks():
            yield "partial"
            raise RuntimeError("stream exploded")

        return _chunks()


class _BytesStreamProvider:
    name = "bytes-stream-provider"

    def complete(self, messages, stream=False):
        if not stream:
            return "unused"
        return b"hi"


def test_stream_provider_iteration_error_emits_error_event_and_done():
    cfg = QuantumLLMConfig(backend="classical", num_qubits=2, shots=64, use_thread=False)
    pipeline = QuantumLLMPipeline(config=cfg)
    pipeline._get_provider = lambda prompt, provider=None: _BrokenStreamProvider()

    async def collect():
        chunks = []
        async for chunk in pipeline.stream("trigger stream failure"):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect())

    assert any('data: {"delta": "partial"}' in chunk for chunk in chunks)
    assert any(chunk.startswith("event: error\n") and "stream exploded" in chunk for chunk in chunks)
    assert any('"quantum_augmented": false' in chunk for chunk in chunks)
    assert chunks[-1].strip() == "data: [DONE]"


def test_stream_provider_iteration_error_with_threaded_provider_call():
    cfg = QuantumLLMConfig(backend="classical", num_qubits=2, shots=64, use_thread=True)
    pipeline = QuantumLLMPipeline(config=cfg)
    pipeline._get_provider = lambda prompt, provider=None: _BrokenStreamProvider()

    async def collect():
        chunks = []
        async for chunk in pipeline.stream("trigger threaded stream failure"):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect())

    assert any(chunk.startswith("event: error\n") and "stream exploded" in chunk for chunk in chunks)
    assert chunks[-1].strip() == "data: [DONE]"


def test_stream_bytes_payload_emits_single_text_delta():
    cfg = QuantumLLMConfig(backend="classical", num_qubits=2, shots=64, use_thread=False)
    pipeline = QuantumLLMPipeline(config=cfg)
    pipeline._get_provider = lambda prompt, provider=None: _BytesStreamProvider()

    async def collect():
        chunks = []
        async for chunk in pipeline.stream("bytes payload"):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect())

    assert sum('data: {"delta": "hi"}' in chunk for chunk in chunks) == 1
    assert not any('"delta": "104"' in chunk or '"delta": "105"' in chunk for chunk in chunks)
    assert chunks[-1].strip() == "data: [DONE]"
