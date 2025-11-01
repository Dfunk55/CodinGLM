"""Terminal interrupt watcher utilities."""

from __future__ import annotations

import os
import select
import sys
import threading
from typing import Optional, Sequence

try:
    import termios
    import tty
except ImportError:  # pragma: no cover - non-POSIX platforms
    termios = None  # type: ignore[assignment]
    tty = None  # type: ignore[assignment]


class StreamInterruptWatcher:
    """Monitor stdin for Esc key to interrupt streaming output."""

    def __init__(self) -> None:
        self._fd: Optional[int] = None
        self._original_attrs: Optional[Sequence[int]] = None  # type: ignore[type-arg]
        self._listener: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._interrupted = threading.Event()

        if sys.stdin.isatty() and termios and tty:
            try:
                self._fd = sys.stdin.fileno()
                self._original_attrs = termios.tcgetattr(self._fd)  # type: ignore[arg-type]
            except Exception:
                self._fd = None
                self._original_attrs = None

    def start(self) -> None:
        """Begin listening for Esc keypress."""
        if self._fd is None or not termios or not tty:
            return

        try:
            tty.setcbreak(self._fd)  # type: ignore[arg-type]
        except Exception:
            self._fd = None
            return

        self._listener = threading.Thread(target=self._listen, daemon=True)
        self._listener.start()

    def _listen(self) -> None:
        """Listen loop for Esc key."""
        if self._fd is None:
            return

        while not self._stop_event.is_set():
            try:
                ready, _, _ = select.select([self._fd], [], [], 0.05)
            except Exception:
                break

            if ready:
                try:
                    data = os.read(self._fd, 1)
                except Exception:
                    break

                if data == b"\x1b":
                    self._interrupted.set()
                    self._stop_event.set()
                    break

        self._stop_event.set()

    def should_stop(self) -> bool:
        """Return True if streaming should be interrupted."""
        return self._interrupted.is_set()

    def stop(self) -> bool:
        """Stop listening and restore terminal state."""
        if self._fd is None:
            return self._interrupted.is_set()

        self._stop_event.set()
        if self._listener:
            self._listener.join(timeout=0.1)

        if self._original_attrs is not None and termios:
            try:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._original_attrs)  # type: ignore[arg-type]
            except Exception:
                pass

        return self._interrupted.is_set()

