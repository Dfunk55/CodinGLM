"""Tests for live markdown streaming helper."""

from __future__ import annotations

import io

from rich.console import Console
from rich.markdown import Markdown

from codinglm.ui.live_markdown import LiveMarkdownStream


def test_live_markdown_stream_updates_and_closes(monkeypatch):
    """Streaming should update markdown output and close the live context."""
    updates = []
    instances = []

    class DummyLive:
        def __init__(self, initial_text, console, refresh_per_second, transient):
            self.initial_text = initial_text
            self.console = console
            self.refresh_per_second = refresh_per_second
            self.transient = transient
            self.closed = False
            instances.append(self)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.closed = True

        def update(self, renderable):
            updates.append(renderable)

    monkeypatch.setattr("codinglm.ui.live_markdown.Live", DummyLive)

    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)
    with LiveMarkdownStream(console) as stream:
        stream.append("Hello")
        stream.append(" world")

    assert stream.content == "Hello world"
    assert len(instances) == 1
    dummy_live = instances[0]
    assert dummy_live.closed is True
    assert len(updates) == 2
    assert all(isinstance(item, Markdown) for item in updates)


def test_append_without_context_buffers_only():
    """Appending outside the context should only store content."""
    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)
    stream = LiveMarkdownStream(console)
    stream.append("")
    stream.append("Line one")
    stream.append("\n")
    stream.append("Line two")

    assert stream.content == "Line one\nLine two"


def test_live_markdown_stream_skips_empty_chunks(monkeypatch):
    """Empty chunks should not trigger live updates."""
    updates = []

    class DummyLive:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def update(self, renderable):
            updates.append(renderable)

    monkeypatch.setattr("codinglm.ui.live_markdown.Live", DummyLive)

    console = Console(file=io.StringIO(), force_terminal=False, color_system=None)
    with LiveMarkdownStream(console) as stream:
        stream.append("")
        stream.append("token")
        stream.append("")

    assert stream.content == "token"
    assert len(updates) == 1
    assert isinstance(updates[0], Markdown)
