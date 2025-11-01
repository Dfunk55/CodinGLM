"""Markdown rendering and UI components."""

from __future__ import annotations

import re
import textwrap

from rich.console import Console, RenderableType
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class MarkdownRenderer:
    """Handles rendering of markdown and code."""

    def __init__(self, console: Console):
        """Initialize renderer.

        Args:
            console: Rich console
        """
        self.console = console

    def render_markdown(self, text: str) -> None:
        """Render markdown text.

        Args:
            text: Markdown text to render
        """
        md = Markdown(text)
        self.console.print(md)

    def render_code(self, code: str, language: str = "python") -> None:
        """Render syntax-highlighted code.

        Args:
            code: Code to render
            language: Programming language
        """
        syntax = Syntax(code, language, theme="monokai")
        self.console.print(syntax)

    def render_error(self, message: str) -> None:
        """Render an error message.

        Args:
            message: Error message
        """
        self.console.print(f"[red]Error: {message}[/red]")

    def render_warning(self, message: str) -> None:
        """Render a warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"[yellow]Warning: {message}[/yellow]")

    def render_info(self, message: str) -> None:
        """Render an info message.

        Args:
            message: Info message
        """
        self.console.print(f"[cyan]{message}[/cyan]")

    def _wrap_markdown_text(self, text: str) -> str:
        """Insert soft line breaks into markdown paragraphs so panels wrap cleanly."""
        width = max(20, (self.console.size.width if self.console.size else self.console.width or 80) - 4)
        wrapped_lines: list[str] = []
        in_code_block = False
        fence_pattern = re.compile(r"^(\s*)(`{3,}|~{3,})")
        list_pattern = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)")
        heading_pattern = re.compile(r"^(\s*#+\s+)(.*)")
        blockquote_pattern = re.compile(r"^(\s*>+\s*)(.*)")

        for original_line in text.splitlines():
            line = original_line.rstrip()

            if not line.strip():
                wrapped_lines.append("")
                continue

            fence_match = fence_pattern.match(line.strip())
            if fence_match:
                in_code_block = not in_code_block
                wrapped_lines.append(line)
                continue

            if in_code_block or line.startswith("    ") or line.startswith("\t"):
                wrapped_lines.append(original_line)
                continue

            if "|" in line and line.count("|") >= 2:
                wrapped_lines.append(line)
                continue

            list_match = list_pattern.match(line)
            if list_match:
                indent, bullet, content = list_match.groups()
                prefix = f"{indent}{bullet} "
                subsequent_indent = " " * len(prefix)
                wrapped_lines.append(
                    textwrap.fill(
                        content,
                        width=width,
                        initial_indent=prefix,
                        subsequent_indent=subsequent_indent,
                        break_long_words=False,
                        replace_whitespace=False,
                        drop_whitespace=False,
                    )
                )
                continue

            heading_match = heading_pattern.match(line)
            if heading_match:
                prefix, content = heading_match.groups()
                wrapped_lines.append(
                    textwrap.fill(
                        content,
                        width=width,
                        initial_indent=prefix,
                        subsequent_indent=" " * len(prefix),
                        break_long_words=False,
                        replace_whitespace=False,
                        drop_whitespace=False,
                    )
                )
                continue

            blockquote_match = blockquote_pattern.match(line)
            if blockquote_match:
                prefix, content = blockquote_match.groups()
                indent = prefix if prefix.endswith(" ") else f"{prefix} "
                wrapped_lines.append(
                    textwrap.fill(
                        content,
                        width=width,
                        initial_indent=indent,
                        subsequent_indent=indent,
                        break_long_words=False,
                        replace_whitespace=False,
                        drop_whitespace=False,
                    )
                )
                continue

            wrapped_lines.append(
                textwrap.fill(
                    line,
                    width=width,
                    break_long_words=False,
                    replace_whitespace=False,
                    drop_whitespace=False,
                )
            )

        return "\n".join(wrapped_lines)

    def render_panel(self, content: RenderableType, title: str, border_style: str = "cyan") -> None:
        """Render content in a panel.

        Args:
            content: Panel content
            title: Panel title
        """
        renderable: RenderableType = content
        if isinstance(renderable, str):
            renderable = Text.from_markup(renderable)

        if isinstance(renderable, (Markdown, Text)):
            table = Table.grid(expand=True)
            table.add_column(ratio=1)
            table.add_row(renderable)
            renderable = table

        panel = Panel(renderable, title=title, border_style=border_style, expand=True)
        self.console.print(panel)

    def render_user_message(self, text: str) -> None:
        """Render a user message in a styled panel."""
        md = Markdown(self._wrap_markdown_text(text))
        self.render_panel(md, "You", border_style="magenta")

    def render_assistant_markdown(self, text: str) -> None:
        """Render assistant markdown in a consistent style."""
        md = Markdown(self._wrap_markdown_text(text))
        self.render_panel(md, "Assistant", border_style="cyan")
