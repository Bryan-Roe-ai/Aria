"""
Unit tests for QuantumLLMConfig dataclass.

Tests configuration validation, environment variable handling, and
safe defaults for quantum LLM pipeline.
"""

import os
import pytest

from ai_projects.quantum_ml.src.quantum_llm.config import (
    QuantumLLMConfig,
    _coerce_float,
    _coerce_int,
    _read_backend_env,
    _read_float_env,
    _read_int_env,
)


class TestIntEnvReading:
    """Test _read_int_env helper."""

    def test_valid_int_env(self, monkeypatch):
        """Should parse valid integer environment variables."""
        monkeypatch.setenv("TEST_INT", "42")
        assert _read_int_env("TEST_INT", 100) == 42

    def test_invalid_int_env_uses_default(self, monkeypatch):
        """Should fall back to default for non-integer env values."""
        monkeypatch.setenv("TEST_INT", "not_a_number")
        assert _read_int_env("TEST_INT", 100) == 100

    def test_missing_int_env_uses_default(self, monkeypatch):
        """Should use default when env var is missing."""
        monkeypatch.delenv("TEST_INT", raising=False)
        assert _read_int_env("TEST_INT", 100) == 100


class TestFloatEnvReading:
    """Test _read_float_env helper."""

    def test_valid_float_env(self, monkeypatch):
        """Should parse valid float environment variables."""
        monkeypatch.setenv("TEST_FLOAT", "3.14")
        assert _read_float_env("TEST_FLOAT", 1.0) == pytest.approx(3.14)

    def test_invalid_float_env_uses_default(self, monkeypatch):
        """Should fall back to default for non-float env values."""
        monkeypatch.setenv("TEST_FLOAT", "not_a_number")
        assert _read_float_env("TEST_FLOAT", 1.0) == 1.0


class TestBackendEnvReading:
    """Test _read_backend_env helper."""

    def test_valid_backends(self, monkeypatch):
        """Should accept valid backend names."""
        for backend in ["auto", "qiskit", "pennylane", "classical"]:
            monkeypatch.setenv("TEST_BACKEND", backend)
            assert _read_backend_env("TEST_BACKEND") == backend

    def test_invalid_backend_uses_default(self, monkeypatch):
        """Should fall back to default for unknown backends."""
        monkeypatch.setenv("TEST_BACKEND", "unknown_backend")
        assert _read_backend_env("TEST_BACKEND", "auto") == "auto"

    def test_missing_backend_uses_default(self, monkeypatch):
        """Should use default when env var is missing."""
        monkeypatch.delenv("TEST_BACKEND", raising=False)
        assert _read_backend_env("TEST_BACKEND", "auto") == "auto"


class TestCoercionHelpers:
    """Test type coercion functions."""

    def test_coerce_int_valid(self):
        """Should convert valid values to int."""
        assert _coerce_int(42, 100) == 42
        assert _coerce_int("42", 100) == 42
        assert _coerce_int(42.9, 100) == 42

    def test_coerce_int_uses_default_on_error(self):
        """Should use default for non-convertible values."""
        assert _coerce_int("not_a_number", 100) == 100
        assert _coerce_int(None, 100) == 100

    def test_coerce_int_respects_minimum(self):
        """Should enforce minimum value."""
        assert _coerce_int(0, 100, minimum=1) == 1
        assert _coerce_int(-10, 100, minimum=1) == 1
        assert _coerce_int(50, 100, minimum=1) == 50

    def test_coerce_float_valid(self):
        """Should convert valid values to float."""
        assert _coerce_float(3.14, 1.0) == pytest.approx(3.14)
        assert _coerce_float("3.14", 1.0) == pytest.approx(3.14)
        assert _coerce_float(3, 1.0) == pytest.approx(3.0)

    def test_coerce_float_uses_default_on_error(self):
        """Should use default for non-convertible values."""
        assert _coerce_float("not_a_number", 1.0) == 1.0
        assert _coerce_float(None, 1.0) == 1.0


class TestQuantumLLMConfigDefaults:
    """Test QuantumLLMConfig with default values."""

    def test_default_config(self):
        """Should create config with sensible defaults."""
        cfg = QuantumLLMConfig()
        assert cfg.backend == "auto"
        assert cfg.num_qubits == 4
        assert cfg.shots == 512
        assert cfg.num_layers == 2
        assert cfg.top_k == 10
        assert cfg.temperature_blend == 0.3
        assert cfg.temperature == 0.7
        assert cfg.max_tokens == 512
        assert cfg.provider == "auto"

    def test_config_normalization(self):
        """Should normalize invalid config values in post_init."""
        cfg = QuantumLLMConfig(
            backend="invalid_backend",
            num_qubits=0,
            shots=-100,
            temperature_blend=1.5,
            temperature=-1.0,
        )
        # Invalid backend should be reset
        assert cfg.backend == "auto"
        # Min/max values should be enforced
        assert cfg.num_qubits >= 1
        assert cfg.shots >= 1
        assert 0.0 <= cfg.temperature_blend <= 1.0
        assert cfg.temperature >= 0.0


class TestQuantumLLMConfigFromEnv:
    """Test QuantumLLMConfig.from_env()."""

    def test_from_env_with_all_vars(self, monkeypatch):
        """Should read all environment variables when set."""
        monkeypatch.setenv("QUANTUM_LLM_BACKEND", "qiskit")
        monkeypatch.setenv("QUANTUM_LLM_QUBITS", "8")
        monkeypatch.setenv("QUANTUM_LLM_SHOTS", "1024")
        monkeypatch.setenv("QUANTUM_LLM_LAYERS", "3")
        monkeypatch.setenv("QUANTUM_LLM_TOP_K", "20")
        monkeypatch.setenv("QUANTUM_LLM_TEMP_BLEND", "0.5")
        monkeypatch.setenv("QUANTUM_LLM_TEMPERATURE", "0.8")
        monkeypatch.setenv("QUANTUM_LLM_MAX_TOKENS", "1024")
        monkeypatch.setenv("QUANTUM_LLM_PROVIDER", "azure")
        monkeypatch.setenv("QUANTUM_LLM_MODEL", "gpt-4")

        cfg = QuantumLLMConfig.from_env()
        assert cfg.backend == "qiskit"
        assert cfg.num_qubits == 8
        assert cfg.shots == 1024
        assert cfg.num_layers == 3
        assert cfg.top_k == 20
        assert cfg.temperature_blend == pytest.approx(0.5)
        assert cfg.temperature == pytest.approx(0.8)
        assert cfg.max_tokens == 1024
        assert cfg.provider == "azure"
        assert cfg.model == "gpt-4"

    def test_from_env_uses_defaults(self, monkeypatch):
        """Should use defaults when environment variables are not set."""
        # Clear all quantum LLM env vars
        for key in [
            "QUANTUM_LLM_BACKEND",
            "QUANTUM_LLM_QUBITS",
            "QUANTUM_LLM_SHOTS",
            "QUANTUM_LLM_LAYERS",
            "QUANTUM_LLM_TOP_K",
            "QUANTUM_LLM_TEMP_BLEND",
            "QUANTUM_LLM_TEMPERATURE",
            "QUANTUM_LLM_MAX_TOKENS",
            "QUANTUM_LLM_PROVIDER",
            "QUANTUM_LLM_MODEL",
        ]:
            monkeypatch.delenv(key, raising=False)

        cfg = QuantumLLMConfig.from_env()
        assert cfg.backend == "auto"
        assert cfg.num_qubits == 4
        assert cfg.shots == 512


class TestQuantumLLMConfigToDict:
    """Test QuantumLLMConfig.to_dict()."""

    def test_to_dict_serialization(self):
        """Should serialize config to dictionary."""
        cfg = QuantumLLMConfig(
            backend="pennylane",
            num_qubits=6,
            shots=256,
            top_k=15,
            temperature_blend=0.4,
            temperature=0.75,
            max_tokens=1024,
            provider="openai",
            model="gpt-3.5-turbo",
        )
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert d["backend"] == "pennylane"
        assert d["num_qubits"] == 6
        assert d["shots"] == 256
        assert d["top_k"] == 15
        assert d["temperature_blend"] == pytest.approx(0.4)
        assert d["temperature"] == pytest.approx(0.75)
        assert d["max_tokens"] == 1024
        assert d["provider"] == "openai"
        assert d["model"] == "gpt-3.5-turbo"

    def test_to_dict_json_serializable(self):
        """Should produce JSON-serializable dictionary."""
        import json

        cfg = QuantumLLMConfig()
        d = cfg.to_dict()
        # Should not raise
        json_str = json.dumps(d)
        assert json_str is not None
