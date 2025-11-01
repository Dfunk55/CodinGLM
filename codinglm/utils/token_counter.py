"""Utilities for estimating token usage."""

from __future__ import annotations

import json
import logging
from typing import Iterable

from ..api.models import Message

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
    _ENCODING = tiktoken.get_encoding("cl100k_base")  # Compatible with Claude/GPT models
except ImportError:
    _TIKTOKEN_AVAILABLE = False
    _ENCODING = None
    logging.debug("tiktoken not available, falling back to heuristic token counting")

# Rough heuristic used in Claude Code clones and other CLI agents.
_AVERAGE_CHARS_PER_TOKEN = 4
_MESSAGE_OVERHEAD_TOKENS = 4


def estimate_text_tokens(text: str | None, use_tiktoken: bool = True) -> int:
    """Estimate token count for a block of text.

    Args:
        text: The text to count tokens for
        use_tiktoken: If True and tiktoken is available, use accurate counting.
                     If False, always use heuristic.

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Use tiktoken if available and requested
    if use_tiktoken and _TIKTOKEN_AVAILABLE and _ENCODING:
        try:
            return len(_ENCODING.encode(text))
        except Exception as e:
            logging.warning(f"tiktoken encoding failed: {e}, falling back to heuristic")

    # Fallback to heuristic
    length = len(text)
    return max(1, (length + _AVERAGE_CHARS_PER_TOKEN - 1) // _AVERAGE_CHARS_PER_TOKEN)


def estimate_message_tokens(message: Message, use_tiktoken: bool = True) -> int:
    """Estimate tokens consumed by a single message.

    Args:
        message: The message to estimate tokens for
        use_tiktoken: If True and tiktoken is available, use accurate counting.
                     If False, always use heuristic.

    Returns:
        Estimated token count
    """
    total = _MESSAGE_OVERHEAD_TOKENS
    total += estimate_text_tokens(message.content, use_tiktoken)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            total += estimate_text_tokens(json.dumps(tool_call, ensure_ascii=False), use_tiktoken)

    if message.tool_call_id:
        total += 2
    if message.name:
        total += 1

    return total


def estimate_messages_tokens(messages: Iterable[Message], use_tiktoken: bool = True) -> int:
    """Estimate total tokens for a sequence of messages.

    Args:
        messages: The messages to estimate tokens for
        use_tiktoken: If True and tiktoken is available, use accurate counting.
                     If False, always use heuristic.

    Returns:
        Total estimated token count
    """
    return sum(estimate_message_tokens(message, use_tiktoken) for message in messages)


def is_tiktoken_available() -> bool:
    """Check if tiktoken is available for accurate token counting.

    Returns:
        True if tiktoken is installed and loaded successfully
    """
    return _TIKTOKEN_AVAILABLE


__all__ = [
    "estimate_message_tokens",
    "estimate_messages_tokens",
    "estimate_text_tokens",
    "is_tiktoken_available",
]
