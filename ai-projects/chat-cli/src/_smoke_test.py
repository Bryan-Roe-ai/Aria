"""Smoke test for chat provider functionality."""
from __future__ import annotations

from importlib import import_module
from typing import Any


def _detect_provider() -> Any:
    module = import_module("chat_providers")
    provider_fn: Any | None = getattr(
        module, "detect_provider", None
    )  # type: ignore
    if provider_fn is not None:
        return provider_fn

    for module_name in (
        "chat_providers.detect",
        "chat_providers.provider",
        "chat_providers.providers",
    ):
        try:
            module = import_module(module_name)
        except ImportError:
            continue

        provider_fn = getattr(module, "detect_provider", None)  # type: ignore
        if provider_fn is not None:
            return provider_fn

    raise RuntimeError("detect_provider is unavailable")


def main() -> int:
    """Run a quick smoke test against the detected chat provider."""
    provider, info = _detect_provider()(explicit="local")
    messages = [
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "Say one short sentence about AI."},
    ]
    result = provider.complete(messages, stream=False)
    assert isinstance(result, str)
    print("Smoke test provider:", info)
    print("Reply:", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
