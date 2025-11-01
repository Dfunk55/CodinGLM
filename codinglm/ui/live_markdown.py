"""Live markdown streaming utilities."""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown


class LiveMarkdownStream:
    """Incrementally render markdown during streaming responses."""

    def __init__(self, console: Console) -> None:
        self._console = console
        self._buffer: list[str] = []
        self._live: Optional[Live] = None

    def __enter__(self) -> "LiveMarkdownStream":
        self._live = Live(
            "",
            console=self._console,
            refresh_per_second=12,
            transient=True,
        )
        self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._live:
            self._live.__exit__(exc_type, exc, tb)
            self._live = None

    def append(self, text: str) -> None:
        """Append text and refresh the display."""
        if not text:
            return

        self._buffer.append(text)
        if self._live:
            self._live.update(Markdown(self.content))

    @property
    def content(self) -> str:
        return "".join(self._buffer)
