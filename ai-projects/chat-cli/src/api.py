"""Public API for chat-cli module.

This module defines the stable interface for the chat-cli component.
All imports from chat-cli should come through this module.
"""

# Re-export main APIs from internal modules
from .agi_provider import AGIProvider, RoleMessage, create_agi
from .chat_providers import (
    AzureOpenAIChatProvider,
    BaseChatProvider,
    LMStudioChatProvider,
    LocalChatProvider,
    OpenAIChatProvider,
    detect_provider,
)
from .token_utils import count_tokens, estimate_tokens, prune_messages

__all__ = [
    # Chat providers
    "detect_provider",
    "BaseChatProvider",
    "RoleMessage",
    "LocalChatProvider",
    "OpenAIChatProvider",
    "AzureOpenAIChatProvider",
    "LMStudioChatProvider",
    # Token utilities
    "prune_messages",
    "count_tokens",
    "estimate_tokens",
    # AGI provider
    "create_agi",
    "AGIProvider",
]
