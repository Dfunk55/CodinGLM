"""Tests for logging utilities."""

import json
from pathlib import Path

from codinglm.logging import DebugEventLogger, TranscriptConsole


def test_transcript_console_streams_to_file(tmp_path):
    transcript_path = tmp_path / "session.log"
    console = TranscriptConsole(
        transcript_path=transcript_path,
        force_terminal=False,
        color_system=None,
    )

    console.print("Hello", end="")
    assert transcript_path.exists()
    first_capture = transcript_path.read_text()
    assert "Hello" in first_capture

    console.print(" world!")
    second_capture = transcript_path.read_text()
    assert "Hello" in second_capture
    assert "world" in second_capture

    console.close()


def test_transcript_console_transcript_only(tmp_path):
    transcript_path = tmp_path / "session.log"
    console = TranscriptConsole(
        transcript_path=transcript_path,
        force_terminal=False,
        color_system=None,
    )

    console.log_transcript_only("Debug note")
    console.close()

    content = transcript_path.read_text()
    assert "Debug note" in content


def test_debug_event_logger_emits_json(tmp_path):
    events_path = tmp_path / "events.jsonl"
    logger = DebugEventLogger(events_path)

    logger.emit("test_event", "Testing", {"foo": "bar"})
    logger.close()

    content = events_path.read_text().strip().splitlines()
    assert len(content) == 1
    payload = json.loads(content[0])
    assert payload["event"] == "test_event"
    assert payload["message"] == "Testing"
    assert payload["foo"] == "bar"
