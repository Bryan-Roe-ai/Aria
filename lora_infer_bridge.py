"""Compatibility shim for LoRA inference bridge imports.

Re-exports the canonical bridge implementation from
``ai-projects/chat-cli/src/lora_infer_bridge.py``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CANONICAL = Path(__file__).resolve().parent / "ai-projects" / "chat-cli" / "src" / "lora_infer_bridge.py"

_spec = importlib.util.spec_from_file_location("_canonical_lora_infer_bridge_root", _CANONICAL)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load canonical bridge: {_CANONICAL}")

_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)

for _name, _value in _mod.__dict__.items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _value

__all__ = [_n for _n in _mod.__dict__ if not _n.startswith("_")]

# Mirror canonical module identity for downstream monkeypatch consistency.
sys.modules[__name__] = _mod
