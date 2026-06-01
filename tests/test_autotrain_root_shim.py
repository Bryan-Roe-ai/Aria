"""Tests for the root-level autotrain.py deprecation shim.

Importing ``autotrain`` from the repository root is deprecated in favour of
``scripts.autotrain``; the shim must emit a DeprecationWarning and re-export the
canonical public API.
"""

from __future__ import annotations

import importlib.util
import warnings
from pathlib import Path


def _load_root_autotrain():
    path = Path(__file__).parent.parent / "autotrain.py"
    spec = importlib.util.spec_from_file_location("autotrain_root_shim_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        spec.loader.exec_module(module)
    return module, caught


def test_root_autotrain_emits_deprecation_warning():
    _module, caught = _load_root_autotrain()

    messages = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
    assert any("deprecated" in m.lower() for m in messages)


def test_root_autotrain_reexports_public_api():
    module, _caught = _load_root_autotrain()

    import scripts.autotrain as canonical

    assert hasattr(module, "__all__")
    for name in ("load_config", "load_jobs", "validate_job", "build_command", "main"):
        assert hasattr(module, name), f"missing re-exported symbol: {name}"
        # Re-exports must be the canonical objects, not local placeholders.
        assert getattr(module, name) is getattr(canonical, name)
