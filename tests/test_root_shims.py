"""Tests for the root-level compatibility shims.

The repo-root ``chat_providers.py`` and ``lora_infer_bridge.py`` files load the
canonical implementations from ``ai-projects/chat-cli/src`` and re-export their
full symbol surface so legacy ``import chat_providers`` paths keep working.

These tests load the root shim files explicitly by path so the assertions are
deterministic regardless of sys.path ordering (a plain ``import chat_providers``
may otherwise resolve to the canonical module when its src dir is on sys.path).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_root_shim(filename: str, module_name: str):
    path = REPO_ROOT / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_chat_providers_root_shim_reexports_core_symbols():
    mod = _load_root_shim("chat_providers.py", "chat_providers_root_shim_under_test")

    # The shim must re-export the canonical provider surface.
    assert hasattr(mod, "LocalEchoProvider")
    assert hasattr(mod, "AzureOpenAIProvider")
    assert hasattr(mod, "__all__")
    assert isinstance(mod.__all__, list)
    assert len(mod.__all__) > 0


def test_lora_infer_bridge_root_shim_reexports():
    mod = _load_root_shim("lora_infer_bridge.py", "lora_infer_bridge_root_shim_under_test")

    # Symbols are copied from the canonical bridge into the shim namespace.
    assert hasattr(mod, "__all__")
    assert isinstance(mod.__all__, list)
    # Re-exported names should resolve as real attributes on the shim module.
    for name in mod.__all__:
        assert hasattr(mod, name)
