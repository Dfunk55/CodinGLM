"""Markdown rendering and UI components."""

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel


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

    def render_panel(self, content: str, title: str) -> None:
        """Render content in a panel.

        Args:
            content: Panel content
            title: Panel title
        """
        panel = Panel(content, title=title, border_style="cyan")
        self.console.print(panel)
