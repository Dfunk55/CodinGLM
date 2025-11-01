"""Tests for conversation manager streaming behaviour."""

import io
from typing import List

from rich.console import Console

from codinglm.api.models import Message, StreamChunk
from codinglm.conversation.manager import ConversationManager
from codinglm.tools.base import ToolRegistry


class FakeClient:
    """Minimal client stub providing streaming chunks."""

    def chat(self, messages: List[Message], tools, stream: bool):
        if stream:
            def generator():
                yield StreamChunk(delta="Hello")
                yield StreamChunk(delta=" world")

            return generator()
        return "completed"

    def create_tool_result_message(self, result):  # pragma: no cover - unused
        raise NotImplementedError


def test_streaming_interrupt_returns_partial_response(monkeypatch):
    """Streaming should respect external stop signal."""
    console_buffer = io.StringIO()
    console = Console(file=console_buffer, force_terminal=False, color_system=None)

    manager = ConversationManager(
        client=FakeClient(),
        registry=ToolRegistry(),
        console=console,
    )
    manager.add_user_message("Say hello")

    call_count = {"count": 0}

    def should_stop() -> bool:
        call_count["count"] += 1
        return call_count["count"] >= 1

    response = manager.run_turn(stream=True, should_stop=should_stop)

    assert response == "Hello"
    assert manager.messages[-1].content == "Hello"
    assert "Hello" in console_buffer.getvalue()
