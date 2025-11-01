"""Logging utilities for CodinGLM."""

from __future__ import annotations

import io
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from rich.console import Console


class TranscriptConsole(Console):
    """Console that mirrors output to a transcript file as it is written.

    The console retains Rich's rendering for the terminal while draining the
    captured output to the transcript file on every print/log call so that
    sessions survive crashes and long conversations without unbounded memory
    growth.
    """

    def __init__(
        self,
        *,
        transcript_path: Optional[Path],
        **kwargs: Any,
    ) -> None:
        self._transcript_path = transcript_path
        self._transcript_lock = threading.Lock()
        self._transcript_handle: Optional[io.TextIOBase] = None
        if transcript_path is not None:
            transcript_path.parent.mkdir(parents=True, exist_ok=True)
            self._transcript_handle = transcript_path.open("a", encoding="utf-8")

        # Record is only needed when we have a transcript destination since we
        # immediately drain the buffer after each print/log call.
        kwargs.setdefault("record", self._transcript_handle is not None)
        super().__init__(**kwargs)

    @property
    def transcript_path(self) -> Optional[Path]:
        """Path backing the transcript or None if disabled."""
        return self._transcript_path

    def log_transcript_only(self, text: str) -> None:
        """Write text directly to the transcript without rendering to the terminal."""
        if not self._transcript_handle:
            return

        line = text if text.endswith("\n") else f"{text}\n"
        with self._transcript_lock:
            self._transcript_handle.write(line)
            self._transcript_handle.flush()

    def print(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        super().print(*args, **kwargs)
        self._drain_transcript()

    def log(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        super().log(*args, **kwargs)
        self._drain_transcript()

    def close(self) -> None:
        """Close the underlying transcript stream."""
        try:
            self._drain_transcript()
        finally:
            if self._transcript_handle:
                self._transcript_handle.close()
                self._transcript_handle = None

    def _drain_transcript(self) -> None:
        """Write the accumulated Rich buffer to the transcript file."""
        if not self._transcript_handle:
            return

        with self._transcript_lock:
            chunk = Console.export_text(self, clear=True)
            if not chunk:
                return
            self._transcript_handle.write(chunk)
            self._transcript_handle.flush()


class DebugEventLogger:
    """Write structured JSON events for deterministic debug analysis."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._lock = threading.Lock()
        self._handle = path.open("a", encoding="utf-8")

    @property
    def path(self) -> Path:
        """Return the underlying JSONL file path."""
        return self._path

    def emit(self, event: str, message: str, extra: Optional[Mapping[str, Any]] = None) -> None:
        """Append a JSONL record with the provided payload."""
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "message": message,
        }
        if extra:
            payload.update(extra)

        line = json.dumps(payload, ensure_ascii=False)
        with self._lock:
            self._handle.write(line + "\n")
            self._handle.flush()

    def close(self) -> None:
        """Close the JSONL stream."""
        with self._lock:
            self._handle.close()
