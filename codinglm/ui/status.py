"""Status helpers for tracking long-running operations."""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.status import Status


class TurnStatus:
    """Manage Rich status display during a conversation turn."""

    def __init__(self, console: Console):
        self._console = console
        self._status_cm: Optional[Status] = None
        self._status: Optional[Status] = None

    def start(self, message: str) -> None:
        """Begin status display."""
        if self._status_cm is not None:
            return
        self._status_cm = self._console.status(message, spinner="dots")
        self._status = self._status_cm.__enter__()

    def update(self, message: str) -> None:
        """Update message text."""
        if self._status:
            self._status.update(message)

    def stop(self) -> None:
        """Stop the status display."""
        if self._status_cm:
            self._status_cm.__exit__(None, None, None)
            self._status_cm = None
            self._status = None

    def __enter__(self) -> "TurnStatus":
        self.start("Preparing response…")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

