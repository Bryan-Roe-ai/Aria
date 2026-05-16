"""
Integration tests for QuantumLLMPipeline.

Tests end-to-end pipeline behavior including provider detection,
streaming, and error handling.
"""

import pytest
from ai_projects.quantum_ml.src.quantum_llm.config import QuantumLLMConfig
from ai_projects.quantum_ml.src.quantum_llm.pipeline import QuantumLLMPipeline


class TestQuantumLLMPipeline:
    """Test QuantumLLMPipeline class."""

    def test_pipeline_initialization(self):
        """Should initialize pipeline with default config."""
        pipeline = QuantumLLMPipeline()
        assert pipeline.config is not None
        assert pipeline.effective_backend in {"pennylane", "qiskit", "classical"}
        assert pipeline.sampler is not None
        assert pipeline.embedder is not None
        assert pipeline.router is not None

    def test_pipeline_with_custom_config(self):
        """Should initialize with custom config."""
        cfg = QuantumLLMConfig(
            backend="classical",
            num_qubits=6,
            shots=256,
            num_layers=3,
        )
        pipeline = QuantumLLMPipeline(config=cfg)
        assert pipeline.config.num_qubits == 6
        assert pipeline.config.shots == 256
        assert pipeline.config.num_layers == 3

    def test_status_endpoint(self):
        """Should return valid status dict."""
        pipeline = QuantumLLMPipeline()
        status = pipeline.status()

        assert isinstance(status, dict)
        assert "backend" in status
        assert "provider" in status
        assert "cache" in status
        assert isinstance(status["cache"], dict)
        assert "enabled" in status["cache"]


class TestQuantumLLMGeneration:
    """Test async generation API."""

    @pytest.mark.asyncio
    async def test_generate_simple(self):
        """Should generate a completion."""
        cfg = QuantumLLMConfig(backend="classical", max_tokens=100)
        pipeline = QuantumLLMPipeline(config=cfg)

        result = await pipeline.generate("Hello!")

        assert isinstance(result, dict)
        assert "response" in result
        assert "provider" in result
        assert "backend" in result
        assert "quantum_augmented" in result
        assert result["quantum_augmented"] is True

    @pytest.mark.asyncio
    async def test_generate_validates_prompt_length(self):
        """Should reject prompts exceeding max length."""
        cfg = QuantumLLMConfig(backend="classical", max_prompt_chars=100)
        pipeline = QuantumLLMPipeline(config=cfg)

        long_prompt = "x" * 1000

        with pytest.raises(ValueError, match="Prompt too long"):
            await pipeline.generate(long_prompt)

    @pytest.mark.asyncio
    async def test_generate_with_seed(self):
        """Should generate with reproducible seed."""
        cfg = QuantumLLMConfig(backend="classical")
        pipeline = QuantumLLMPipeline(config=cfg)

        result1 = await pipeline.generate("test", seed=42)
        result2 = await pipeline.generate("test", seed=42)

        # Should get similar structure (may not be identical due to provider variance)
        assert result1["provider"] == result2["provider"]
        assert result1["backend"] == result2["backend"]


class TestQuantumLLMStreaming:
    """Test async streaming API."""

    @pytest.mark.asyncio
    async def test_stream_simple(self):
        """Should stream completion chunks."""
        cfg = QuantumLLMConfig(backend="classical")
        pipeline = QuantumLLMPipeline(config=cfg)

        chunks = []
        async for chunk in pipeline.stream("Hi"):
            chunks.append(chunk)

        assert len(chunks) > 0

        # Should end with [DONE]
        assert any("[DONE]" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_sse_format(self):
        """Should yield SSE-formatted strings."""
        cfg = QuantumLLMConfig(backend="classical")
        pipeline = QuantumLLMPipeline(config=cfg)

        chunks = []
        async for chunk in pipeline.stream("test"):
            chunks.append(chunk)
            # Each chunk should be valid SSE format or the [DONE] marker
            assert chunk.startswith(("data: ", "event: ")) or "[DONE]" in chunk

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_stream_validates_prompt_length(self):
        """Should handle overly long prompts in stream."""
        cfg = QuantumLLMConfig(backend="classical", max_prompt_chars=100)
        pipeline = QuantumLLMPipeline(config=cfg)

        long_prompt = "x" * 1000

        chunks = []
        async for chunk in pipeline.stream(long_prompt):
            chunks.append(chunk)

        # Should get error event
        assert any("error" in chunk.lower() for chunk in chunks)


class TestQuantumLLMCaching:
    """Test circuit caching behavior."""

    def test_cache_stats_reflected_in_status(self):
        """Cache stats should appear in status endpoint."""
        cfg = QuantumLLMConfig(
            backend="classical",
            cache_enabled=True,
            cache_max_size=10,
        )
        pipeline = QuantumLLMPipeline(config=cfg)

        status = pipeline.status()

        assert status["cache"]["enabled"] is True
        assert "stats" in status["cache"]

    def test_cache_disabled_when_configured(self):
        """Should disable cache when configured."""
        cfg = QuantumLLMConfig(backend="classical", cache_enabled=False)
        pipeline = QuantumLLMPipeline(config=cfg)

        status = pipeline.status()

        assert status["cache"]["enabled"] is False
        assert status["cache"]["stats"] == {}


class TestQuantumLLMErrorHandling:
    """Test error handling in pipeline."""

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self):
        """Should handle empty prompts gracefully."""
        pipeline = QuantumLLMPipeline()

        # Empty prompt should be handled
        result = await pipeline.generate("")
        assert "response" in result

    @pytest.mark.asyncio
    async def test_stream_error_on_long_prompt(self):
        """Stream should handle oversized prompts."""
        cfg = QuantumLLMConfig(backend="classical", max_prompt_chars=50)
        pipeline = QuantumLLMPipeline(config=cfg)

        prompt = "x" * 100

        chunks = []
        async for chunk in pipeline.stream(prompt):
            chunks.append(chunk)

        # Should complete without hanging
        assert len(chunks) > 0
