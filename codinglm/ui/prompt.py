"""Prompt session helpers for the CodinGLM CLI."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys


class SlashCommandCompleter(Completer):
    """Autocomplete helper for slash commands."""

    def __init__(self, commands: Mapping[str, str]):
        self._commands = dict(commands)

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor
        if not text.startswith("/"):
            return

        segments = text.split()
        prefix = segments[0]
        if not complete_event.completion_requested and len(prefix) <= 1:
            return
        prefix_lower = prefix.lower()

        for command, description in self._commands.items():
            if command.lower().startswith(prefix_lower):
                yield Completion(
                    command,
                    start_position=-len(prefix),
                    display_meta=description,
                )


class PromptSessionFactory:
    """Factory for building configured prompt sessions."""

    def __init__(
        self,
        commands: Mapping[str, str],
        history_path: str,
        extra_key_bindings: Optional[KeyBindings] = None,
    ) -> None:
        self._commands = commands
        self._history_path = history_path
        self._extra_key_bindings = extra_key_bindings

    @staticmethod
    def _build_key_bindings() -> KeyBindings:
        kb = KeyBindings()

        def _register(key, handler):
            try:
                decorator = kb.add(key)
            except ValueError:
                return
            decorator(handler)

        def _insert_newline(event) -> None:
            """Insert newline without submitting."""
            event.current_buffer.insert_text("\n")

        for key in (Keys.ControlJ,):
            _register(key, _insert_newline)

        @kb.add("escape")
        def _(event) -> None:
            """Allow ESC to clear current input quickly."""
            if event.current_buffer.text:
                event.current_buffer.reset()

        return kb

    @staticmethod
    def _bottom_toolbar() -> HTML:
        return HTML(
            "⏎ send    •    <b>Ctrl+J</b> newline"
            "    •    <b>Tab</b> complete slash commands"
        )

    @staticmethod
    def _prompt_continuation(width: int, line_number: int, is_soft_wrap: bool) -> str:
        prompt_char = "·" if is_soft_wrap else "…"
        return f"{prompt_char} "

    def build(self) -> PromptSession:
        """Return a prompt session with history, completions, and key bindings."""
        bindings = [self._build_key_bindings()]
        if self._extra_key_bindings:
            bindings.append(self._extra_key_bindings)

        session = PromptSession(
            history=FileHistory(self._history_path),
            completer=SlashCommandCompleter(self._commands),
            complete_while_typing=True,
            key_bindings=merge_key_bindings(bindings),
            bottom_toolbar=self._bottom_toolbar,
            prompt_continuation=self._prompt_continuation,
        )
        return session
