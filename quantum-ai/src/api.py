"""Public API for the legacy `quantum-ai` module.

This package is a compatibility surface that re-exports the canonical
Quantum Code LLM functionality from `quantum-ai/src/quantum_code_llm.py`.

Use these imports for stable caller contracts:

    from quantum_code_llm import train, generate
    # or
    from api import train, generate
"""

from typing import Any

try:
    # Package import (e.g., import quantum_ai.src.api)
    from . import quantum_code_llm as _quantum_code_llm
except ImportError:
    # Top-level import (e.g., sys.path -> quantum-ai/src; import api)
    import quantum_code_llm as _quantum_code_llm  # type: ignore

_impl: Any = _quantum_code_llm

QUANTUM_BACKEND = _impl.QUANTUM_BACKEND
CodeTokenizer = _impl.CodeTokenizer
QuantumCodeLLM = _impl.QuantumCodeLLM
QuantumCodeLLMConfig = _impl.QuantumCodeLLMConfig
TrainConfig = _impl.TrainConfig
generate = _impl.generate
load_checkpoint = _impl.load_checkpoint
save_checkpoint = _impl.save_checkpoint
train = _impl.train

__all__ = [
    "QUANTUM_BACKEND",
    "CodeTokenizer",
    "QuantumCodeLLM",
    "QuantumCodeLLMConfig",
    "TrainConfig",
    "train",
    "generate",
    "save_checkpoint",
    "load_checkpoint",
]
