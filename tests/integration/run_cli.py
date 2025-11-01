"""Helper script to launch the CodinGLM CLI with a fake GLM client for tests."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from unittest.mock import patch

from codinglm.api.models import Message, StreamChunk, ToolCall


class FakeStreamClient:
    """Minimal GLM client stub that emits a tool call then final text."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "glm-4.6",
        temperature: float = 0.0,
        max_tokens: int = 0,
        base_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        console: Any = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.timeout_ms = timeout_ms
        self.console = console

    def chat(
        self,
        *,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Any:
        last = messages[-1]

        if not stream:
            if last.role == "tool":
                return "Tool output captured."
            return "Acknowledged."

        if last.role == "user" and "smoke" in (last.content or ""):

            def _tool_stream() -> Iterator[StreamChunk]:
                yield StreamChunk(
                    tool_calls=[
                        ToolCall(
                            id="toolu_1",
                            function={
                                "name": "Bash",
                                "arguments": '{"command": "echo integration smoke"}',
                            },
                        )
                    ]
                )
                yield StreamChunk(finish_reason="tool_use")

            return _tool_stream()

        if last.role == "tool":

            def _result_stream() -> Iterator[StreamChunk]:
                yield StreamChunk(delta="Tool output captured.")
                yield StreamChunk(finish_reason="stop")

            return _result_stream()

        def _default_stream() -> Iterator[StreamChunk]:
            yield StreamChunk(delta="Ready.")
            yield StreamChunk(finish_reason="stop")

        return _default_stream()


@contextmanager
def patched_cli() -> Iterator[None]:
    """Patch CLI dependencies for integration tests."""
    class SimplePromptSession:
        def prompt(self, prompt_text: str = "") -> str:
            sys.stdout.write(prompt_text)
            sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:
                raise EOFError
            return line.rstrip("\n")

    class DummyInterruptWatcher:
        def start(self) -> None:
            pass

        def should_stop(self) -> bool:
            return False

        def stop(self) -> bool:
            return False

    with patch("codinglm.cli_app.GLMClient", FakeStreamClient), patch(
        "codinglm.cli_app.radiolist_dialog", None
    ), patch("codinglm.ui.prompt.PromptSessionFactory.build", lambda self: SimplePromptSession()), patch(
        "codinglm.cli_app.StreamInterruptWatcher", lambda: DummyInterruptWatcher()
    ):
        yield


def main(argv: List[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    os.environ.setdefault("Z_AI_API_KEY", "test-key")

    from codinglm.cli import main as cli_main

    with patched_cli():
        sys.argv = ["codinglm", *argv]
        cli_main()


if __name__ == "__main__":
    main()
