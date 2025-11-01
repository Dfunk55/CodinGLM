"""Tests for /compact command."""

import io
from pathlib import Path

import pytest
from rich.console import Console

from codinglm.api.models import Message
from codinglm.cli import CodinGLMCLI
from codinglm.config import Config, ContextCompressionConfig


@pytest.fixture
def cli(monkeypatch) -> CodinGLMCLI:
    """Create a CLI instance with stubbed prompt session."""

    class DummySession:
        def __init__(self, *args, **kwargs):
            pass

        def prompt(self, *args, **kwargs):
            raise RuntimeError("prompt should not be used in tests")

    monkeypatch.setattr("codinglm.cli.PromptSession", DummySession)

    config = Config(
        apiKey="test-key",
        model="glm-4.6",
    )
    # Configure compression with low limits for testing
    config.context.compression = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=500,
        targetContextTokens=300,
        preserveRecentMessages=2,
        verbose=False,
    )

    return CodinGLMCLI(config=config, cwd=Path.cwd(), debug=False)


def test_compact_command_no_compression_needed(cli: CodinGLMCLI) -> None:
    """Test /compact when compression is not needed."""
    # Add just a few messages - below the limit
    cli.conversation.messages.append(Message(role="user", content="Hello"))
    cli.conversation.messages.append(Message(role="assistant", content="Hi there!"))

    # Call compact command
    cli._handle_compact_command()

    # Should not remove any messages
    assert len(cli.conversation.messages) >= 3  # system + 2 messages


def test_compact_command_with_compression(cli: CodinGLMCLI, monkeypatch) -> None:
    """Test /compact when compression is triggered."""
    # Mock the summarization to avoid API calls
    def mock_summarize(messages):
        return "Summary of previous conversation"

    monkeypatch.setattr(
        cli.conversation.compressor,
        "_summarize_override",
        mock_summarize
    )

    # Add many messages to exceed the limit
    for i in range(20):
        cli.conversation.messages.append(
            Message(role="user", content=f"Message {i} " + "x" * 100)
        )
        cli.conversation.messages.append(
            Message(role="assistant", content=f"Response {i} " + "y" * 100)
        )

    messages_before = len(cli.conversation.messages)

    # Call compact command
    cli._handle_compact_command()

    messages_after = len(cli.conversation.messages)

    # Should have removed some messages
    assert messages_after < messages_before


def test_compact_command_output_format(cli: CodinGLMCLI, monkeypatch) -> None:
    """Test that /compact provides clear feedback."""
    # Capture console output
    buffer = io.StringIO()
    cli.console = Console(file=buffer, force_terminal=False, color_system=None)

    # Add just a few messages
    cli.conversation.messages.append(Message(role="user", content="Test"))

    # Call compact command
    cli._handle_compact_command()

    output = buffer.getvalue()

    # Should mention no compression or show status
    assert "tokens" in output.lower()
    assert "messages" in output.lower()


def test_compact_command_via_handle_command(cli: CodinGLMCLI) -> None:
    """Test that /compact works through the command handler."""
    # Add some messages
    cli.conversation.messages.append(Message(role="user", content="Test message"))

    messages_before = len(cli.conversation.messages)

    # Call via command handler
    cli._handle_command("/compact")

    # Should not crash
    messages_after = len(cli.conversation.messages)
    assert messages_after >= 1  # At least system message


def test_metrics_command_reports_metrics(cli: CodinGLMCLI) -> None:
    """Test that /metrics displays compression statistics."""
    cli.conversation.compressor.metrics.record_compression(
        tokens_before=1000,
        tokens_after=600,
        messages_count=5,
        used_api=True,
    )

    buffer = io.StringIO()
    cli.console = Console(file=buffer, force_terminal=False, color_system=None)

    cli._handle_metrics_command()

    output = buffer.getvalue()
    assert "Compression Metrics" in output
    assert "Compressions: 1" in output
    assert "Tokens saved" in output
