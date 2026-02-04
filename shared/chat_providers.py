"""Re-export chat providers from src.chat module.

This provides a unified import point for chat providers used throughout the workspace.
Supports LMStudio, LoRA adapters, Azure OpenAI, OpenAI, and local fallback.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add src/chat to path for importing
package_root = Path(__file__).resolve().parent.parent / "src" / "chat"
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

from chat_providers import (  # type: ignore
    RoleMessage,
    ProviderChoice,
    BaseChatProvider,
    LocalEchoProvider,
    OpenAIProvider,
    AzureOpenAIProvider,
    detect_provider,
)

__all__ = [
    "RoleMessage",
    "ProviderChoice",
    "BaseChatProvider",
    "LocalEchoProvider",
    "OpenAIProvider",
    "AzureOpenAIProvider",
    "detect_provider",
]

try:  # Optional providers
    from chat_providers import LoraLocalProvider  # type: ignore
    LoraLocalProvider
    __all__.append("LoraLocalProvider")
except Exception:
    pass

try:
    from chat_providers import LMStudioProvider  # type: ignore
    LMStudioProvider
    __all__.append("LMStudioProvider")
except Exception:
    pass

try:
    from chat_providers import AGIProvider, AGIContext, ReasoningStep, create_agi_provider  # type: ignore
    __all__.extend([
        "AGIProvider",
        "AGIContext",
        "ReasoningStep",
        "create_agi_provider",
    ])
except Exception:
    pass


