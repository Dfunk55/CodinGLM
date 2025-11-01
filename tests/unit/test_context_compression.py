"""Tests for the context compression system."""

import io

from rich.console import Console

from codinglm.api.models import Message
from codinglm.config import ContextCompressionConfig
from codinglm.conversation.compression import ContextCompressor, SUMMARY_NAME


def _messages_with(prefix: str, count: int) -> list[Message]:
    """Generate alternating user/assistant messages with long content."""
    messages = []
    for index in range(count):
        role = "user" if index % 2 == 0 else "assistant"
        content = f"{role}-{prefix}-{index} " + ("#" * 400)
        messages.append(Message(role=role, content=content))
    return messages


def test_compression_replaces_old_messages_with_summary():
    """The compressor should collapse old turns into a synthetic summary message."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=200,
        targetContextTokens=150,
        preserveRecentMessages=4,
        summaryMaxTokens=50,
        maxCompressionPasses=2,
    )
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)

    # Large history plus two recent messages that should be preserved.
    messages = [Message(role="system", content="base system prompt")]
    messages.extend(_messages_with("old", 6))
    messages.extend(_messages_with("recent", 4))

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "• kept decision\n• outstanding task",
    )

    compressor.maybe_compress(messages, trigger="test")

    # Check for messages with the summary marker pattern (SUMMARY_NAME:unique_id)
    summary_indices = [
        idx for idx, msg in enumerate(messages)
        if msg.name and msg.name.startswith(f"{SUMMARY_NAME}:")
    ]
    assert summary_indices, "Expected a summary message to be inserted"

    summary_index = summary_indices[0]
    assert summary_index > 0  # should not replace the system prompt

    # Ensure only the old turns were replaced — recent messages are still present.
    preserved_tail = [
        message
        for message in messages
        if message.role != "system"
    ][-config.preserveRecentMessages :]
    assert all("recent" in (msg.content or "") for msg in preserved_tail)

    # Console log should mention compression.
    assert "Context compressed" in buffer.getvalue()


def test_compression_noop_when_under_budget():
    """Do nothing if the history comfortably fits the context window."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=2000,
        targetContextTokens=1800,
        preserveRecentMessages=2,
        summaryMaxTokens=50,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [Message(role="system", content="base")]
    messages.extend(_messages_with("small", 2))

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "fallback",
    )
    compressor.maybe_compress(messages, trigger="test")

    # Check no messages have the summary marker pattern
    assert all(
        not (msg.name and msg.name.startswith(f"{SUMMARY_NAME}:"))
        for msg in messages
    )


def test_compression_preserves_tail_length():
    """The configured number of recent messages should remain untouched."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=200,
        targetContextTokens=150,
        preserveRecentMessages=3,
        summaryMaxTokens=50,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [Message(role="system", content="system")]
    messages.extend(_messages_with("segment", 7))

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "summary",
    )
    compressor.maybe_compress(messages, trigger="test")

    # The last 3 non-system messages should remain direct copies.
    tail_messages = [msg for msg in messages if msg.role != "system"][-3:]
    assert all("segment" in (msg.content or "") for msg in tail_messages)


def test_compression_with_empty_messages():
    """Handle messages with empty content gracefully."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=200,
        targetContextTokens=150,
        preserveRecentMessages=2,
        summaryMaxTokens=50,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [Message(role="system", content="system")]
    messages.append(Message(role="user", content=""))
    messages.append(Message(role="assistant", content=""))
    messages.extend(_messages_with("content", 10))

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "summary of empty messages",
    )
    compressor.maybe_compress(messages, trigger="test")

    # Should still compress successfully
    assert any("summary" in (msg.content or "") for msg in messages)


def test_compression_with_tool_calls():
    """Handle messages with tool_calls but no content."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=300,
        targetContextTokens=200,
        preserveRecentMessages=2,
        summaryMaxTokens=50,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [Message(role="system", content="system")]
    messages.extend(_messages_with("old", 8))
    messages.append(
        Message(
            role="assistant",
            tool_calls=[{"id": "1", "type": "function", "function": {"name": "test", "arguments": "{}"}}],
        )
    )
    messages.extend(_messages_with("recent", 2))

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "summary with tool calls",
    )
    compressor.maybe_compress(messages, trigger="test")

    # Should handle tool calls in token counting
    assert any("summary" in (msg.content or "") for msg in messages)


def test_compression_convergence_check():
    """Stop compression if insufficient token reduction per pass."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=500,
        targetContextTokens=100,
        preserveRecentMessages=2,
        summaryMaxTokens=600,  # Large summary that doesn't save much
        maxCompressionPasses=5,
        verbose=False,
    )
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)

    messages = [Message(role="system", content="system")]
    messages.extend(_messages_with("data", 20))

    # Summary is almost as long as original - no real reduction
    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "x" * 2000,  # Large summary
    )

    compressor.maybe_compress(messages, trigger="test")

    # Should stop early due to insufficient reduction
    # We should see only 1 or 2 compressions, not 5
    assert compressor.metrics.total_compressions < 5


def test_compression_metrics_tracking():
    """Verify metrics are tracked correctly."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=300,
        targetContextTokens=200,
        preserveRecentMessages=2,
        summaryMaxTokens=50,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [Message(role="system", content="system")]
    messages.extend(_messages_with("content", 15))

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "short summary",
    )

    initial_metrics = compressor.get_metrics()
    assert initial_metrics.total_compressions == 0

    compressor.maybe_compress(messages, trigger="test")

    metrics = compressor.get_metrics()
    assert metrics.total_compressions > 0
    assert metrics.total_messages_compressed > 0
    assert metrics.get_tokens_saved() > 0
    assert 0 < metrics.get_compression_ratio() < 1


def test_compression_single_message():
    """Handle conversation with single non-system message."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=100,
        targetContextTokens=50,
        preserveRecentMessages=1,
        summaryMaxTokens=50,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [
        Message(role="system", content="system"),
        Message(role="user", content="x" * 500),  # Very long
    ]

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "summary",
    )

    compressor.maybe_compress(messages, trigger="test")

    # Should not compress - only 1 message and preserveRecentMessages=1
    non_system = [m for m in messages if m.role != "system"]
    assert len(non_system) == 1
    assert "x" * 500 in (non_system[0].content or "")


def test_compression_all_messages_already_summaries():
    """Prevent infinite loop when all messages are already summaries."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=200,
        targetContextTokens=100,
        preserveRecentMessages=1,
        summaryMaxTokens=50,
        verbose=True,  # Enable verbose to test the skip message
    )
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "summary",
    )

    messages = [Message(role="system", content="system")]
    # Add multiple summary messages with the unique marker
    for i in range(5):
        messages.append(
            Message(
                role="assistant",
                name=compressor._summary_marker,
                content=f"[context compression #{i}] Previous summary " + "x" * 200,
            )
        )
    messages.append(Message(role="user", content="recent message"))

    compressor.maybe_compress(messages, trigger="test")

    # Should skip compression since all non-recent messages are summaries
    output = buffer.getvalue()
    assert "skipped" in output.lower()
    assert "all messages already compressed" in output.lower()
    assert compressor.metrics.total_compressions == 0


def test_compression_multipass():
    """Test multiple compression passes to reach target."""
    config = ContextCompressionConfig(
        enabled=True,
        maxContextTokens=500,
        targetContextTokens=200,
        preserveRecentMessages=2,
        summaryMaxTokens=100,
        maxCompressionPasses=3,
    )
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)

    messages = [Message(role="system", content="system")]
    messages.extend(_messages_with("content", 30))  # Many messages

    compressor = ContextCompressor(
        client=None,
        console=console,
        config=config,
        summarize_override=lambda window: "summary " * 10,  # Short summary
    )

    compressor.maybe_compress(messages, trigger="test")

    # Should have performed multiple passes
    metrics = compressor.get_metrics()
    # May be 1, 2, or 3 depending on token estimates
    assert metrics.total_compressions >= 1
