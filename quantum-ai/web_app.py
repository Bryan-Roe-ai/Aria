"""Compatibility wrapper for the quantum web app module.

The canonical implementation lives in:
    ai-projects/quantum-ml/web_app.py

This wrapper preserves legacy import paths used by tests and scripts.
It also hardens checkpoint loading for security and error handling.
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    import numpy as _LOCAL_NUMPY
except ImportError:
    _LOCAL_NUMPY = None

_CANONICAL = Path(__file__).resolve().parents[1] / "ai-projects" / "quantum-ml" / "web_app.py"

if not _CANONICAL.exists():
    raise FileNotFoundError(f"Canonical web app not found: {_CANONICAL}")

_spec = importlib.util.spec_from_file_location(
    "_canonical_quantum_web_app",
    _CANONICAL,
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load spec for {_CANONICAL}")

_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)


def _get_logger() -> logging.Logger:
    """Return canonical logger when available, otherwise a fallback logger."""
    try:
        # Prefer Flask app logger when present.
        app = getattr(_mod, "app", None)
        if app is not None and hasattr(app, "logger"):
            return app.logger
    except (AttributeError, RuntimeError, TypeError):
        pass
    return logging.getLogger("quantum-ai.web_app")


def _get_request_json() -> dict[str, Any]:
    """Safely obtain JSON payload from the canonical module's request object.

    Returns an empty dict if request/json are unavailable or malformed.
    """
    try:
        req = getattr(_mod, "request", None)
        if req is None:
            return {}
        # request.get_json(silent=True) is safer than accessing .json directly.
        if hasattr(req, "get_json"):
            payload = req.get_json(silent=True) or {}
            if isinstance(payload, Mapping):
                return dict(payload)
            return {}

        payload = getattr(req, "json", {}) or {}
        if isinstance(payload, Mapping):
            return dict(payload)
        return {}
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return {}


def _is_within_directory(child: Path, parent: Path) -> bool:
    """Return True if child is inside parent directory.

    Uses pathlib.Path.relative_to when available; falls back to parent
    membership check.
    """
    try:
        child_resolved = child.resolve()
        parent_resolved = parent.resolve()
    except (OSError, RuntimeError):
        return False

    # Python 3.9+: is_relative_to
    if hasattr(child_resolved, "is_relative_to"):
        try:
            return child_resolved.is_relative_to(parent_resolved)
        except (AttributeError, TypeError, ValueError):
            return False

    try:
        child_resolved.relative_to(parent_resolved)
        return True
    except (TypeError, ValueError):
        return False


def _to_mapping(value: Any) -> dict[str, Any] | None:
    """Best-effort conversion of unknown data into a plain dictionary."""
    if isinstance(value, dict):
        return value

    if isinstance(value, Mapping):
        return {str(k): v for k, v in value.items()}

    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], Mapping):
        return {str(k): v for k, v in value[0].items()}

    try:
        return dict(value)
    except (TypeError, ValueError):
        return None


def _normalize_shape(weights: Any) -> list[int]:
    """Return a JSON-safe shape list from a weights object when available."""
    shape = getattr(weights, "shape", None)
    if shape is None:
        return []

    try:
        return [int(dim) for dim in shape]
    except (TypeError, ValueError):
        return []


def _json_error(message: str, status: int) -> Any:
    """Return a consistent JSON error response tuple."""
    return _mod.jsonify({"error": message}), status


# pylint: disable=too-many-locals,too-many-return-statements
# pylint: disable=too-many-branches,too-many-statements
def _compat_load_checkpoint() -> Any:
    """Compatibility endpoint using the legacy quantum-ai
    checkpoints directory.

        Expected JSON payload:
        {
            "checkpoint_path": (
                "relative/or/absolute/path/to/checkpoint"
            )
        }

    Security:
        - Only allows checkpoint files contained in the repo's
            `quantum-ai/checkpoints` directory.
        - Performs strong path resolution and membership checks to avoid
            directory traversal.

    Error handling:
        - Returns concise error messages to callers and logs full tracebacks to
            the application logger.
    """
    logger = _get_logger()
    payload = _get_request_json()
    checkpoint_path = payload.get("checkpoint_path")

    if not isinstance(checkpoint_path, str) or not checkpoint_path.strip():
        return _json_error("No checkpoint path provided", 400)

    try:
        requested_path = Path(checkpoint_path)
        checkpoint_dir = Path(__file__).resolve().parent / "checkpoints"

        if not requested_path.is_absolute():
            requested_path = checkpoint_dir / requested_path

        # Normalize and resolve paths; fail when resolution fails.
        try:
            resolved_path = requested_path.resolve()
            allowed_dir = checkpoint_dir.resolve()
        except (OSError, RuntimeError) as e:
            logger.debug("Path resolution failed: %s", e)
            return _json_error("Invalid checkpoint path", 400)

        if not _is_within_directory(resolved_path, allowed_dir):
            return _json_error(
                "Invalid checkpoint path: must be within checkpoints directory",
                403,
            )

        if not resolved_path.exists() or not resolved_path.is_file():
            return _json_error("Checkpoint file not found", 404)

        # Prefer NumPy from canonical module to preserve behavior.
        np = getattr(_mod, "np", None)
        if np is None:
            np = _LOCAL_NUMPY

        if np is None:
            logger.error("NumPy is required to load checkpoints.")
            return _json_error(
                "Server misconfiguration: NumPy not available",
                500,
            )

        # Attempt load without pickles first.
        allow_pickle = False
        try:
            checkpoint = np.load(str(resolved_path), allow_pickle=False)
        except (
            AttributeError,
            EOFError,
            OSError,
            TypeError,
            ValueError,
        ) as exc_no_pickle:
            logger.debug(
                "Initial np.load without pickles failed: %s",
                exc_no_pickle,
            )
            # Retry with allow_pickle=True as a compatibility fallback.
            try:
                checkpoint = np.load(str(resolved_path), allow_pickle=True)
                allow_pickle = True
                logger.warning(
                    "Loaded checkpoint with allow_pickle=True for %s",
                    resolved_path,
                )
            except (
                AttributeError,
                EOFError,
                OSError,
                TypeError,
                ValueError,
            ) as exc_with_pickle:
                logger.exception(
                    "Failed to load checkpoint file: %s",
                    exc_with_pickle,
                )
                return _json_error("Failed to load checkpoint file", 500)

        data: dict[str, Any] | None = None
        if hasattr(checkpoint, "files"):
            try:
                data = {name: checkpoint[name] for name in checkpoint.files}
            except (AttributeError, KeyError, TypeError, ValueError) as e_read:
                if allow_pickle:
                    logger.exception(
                        "Unexpected checkpoint structure for %s",
                        resolved_path,
                    )
                    return _json_error("Unexpected checkpoint format", 500)

                logger.debug(
                    "Reading checkpoint members failed (%s); retry with pickles",
                    e_read,
                )
                try:
                    checkpoint = np.load(str(resolved_path), allow_pickle=True)
                    allow_pickle = True
                    data = {name: checkpoint[name] for name in checkpoint.files}
                except (
                    AttributeError,
                    KeyError,
                    OSError,
                    TypeError,
                    ValueError,
                ) as e_retry:
                    logger.exception(
                        "Failed to read checkpoint after retry: %s",
                        e_retry,
                    )
                    return _json_error("Unexpected checkpoint format", 500)
        elif isinstance(checkpoint, np.ndarray) and checkpoint.dtype == object:
            data = _to_mapping(checkpoint.tolist())
        else:
            data = _to_mapping(checkpoint)

        if data is None:
            logger.exception(
                "Unexpected checkpoint structure for %s",
                resolved_path,
            )
            return _json_error("Unexpected checkpoint format", 500)

        # Validate required keys
        if not ("weights" in data and "epoch" in data):
            logger.debug(
                "Checkpoint missing required keys: %s",
                list(data.keys()),
            )
            return _json_error(
                "Checkpoint missing required keys (weights, epoch)",
                400,
            )

        weights = data["weights"]
        epoch_val = data["epoch"]
        try:
            epoch = int(epoch_val)
        except (TypeError, ValueError):
            logger.debug("Invalid epoch value in checkpoint: %r", epoch_val)
            return _json_error("Invalid epoch value in checkpoint", 400)

        # Config may be stored as an array or mapping.
        config = data.get("config")
        if config is not None and hasattr(config, "item"):
            try:
                config = config.item()
            except (AttributeError, TypeError, ValueError):
                pass

        response = {
            "success": True,
            "weights_shape": _normalize_shape(weights),
            "epoch": epoch,
            "config": config,
            "message": f"Checkpoint loaded from epoch {epoch}",
            "meta": {"loaded_with_allow_pickle": bool(allow_pickle)},
        }

        return _mod.jsonify(response)

    except (
        AttributeError,
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        # Log traceback for diagnostics; return a concise error to caller.
        logger.exception("Unhandled error while loading checkpoint: %s", exc)
        return _json_error(
            "Internal server error while loading checkpoint",
            500,
        )


# Keep route path and endpoint name stable while swapping handler logic
# to use the legacy checkpoint root expected by existing callers.
try:
    _mod.app.view_functions["load_checkpoint"] = _compat_load_checkpoint
except (AttributeError, KeyError, TypeError):
    # If canonical module does not expose `app`, keep direct import fallback.
    pass

# Re-export public symbols for compatibility.
for _name, _value in list(_mod.__dict__.items()):
    if not _name.startswith("__"):
        globals()[_name] = _value

load_checkpoint = _compat_load_checkpoint
