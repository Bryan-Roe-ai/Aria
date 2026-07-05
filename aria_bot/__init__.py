"""Repository-root compatibility shim for the canonical ``aria_bot`` package.

Allows ``import aria_bot`` and ``python -m aria_bot`` to work from the repo
root while the canonical implementation continues to live under
``aria-bot/aria_bot``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CANONICAL_PACKAGE = Path(__file__).resolve().parent.parent / "aria-bot" / "aria_bot"
_CANONICAL_INIT = _CANONICAL_PACKAGE / "__init__.py"

if not _CANONICAL_INIT.exists():
    raise ImportError(f"Unable to load canonical aria_bot package: {_CANONICAL_INIT}")

__path__ = [str(_CANONICAL_PACKAGE)]

_spec = importlib.util.spec_from_file_location(
    "_canonical_aria_bot_root",
    _CANONICAL_INIT,
    submodule_search_locations=__path__,
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load canonical aria_bot package: {_CANONICAL_INIT}")

_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

for _name, _value in _module.__dict__.items():
    if _name.startswith("__") and _name not in {"__all__", "__doc__"}:
        continue
    globals()[_name] = _value

if hasattr(_module, "__all__"):
    globals()["__all__"] = list(_module.__all__)  # type: ignore[attr-defined]
else:
    _exported_names = [name for name in globals() if not name.startswith("__")]
    globals()["__all__"] = _exported_names
