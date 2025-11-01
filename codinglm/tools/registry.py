"""Default tool registry with all available tools."""

from .base import ToolRegistry
from .file_ops import Read, Write, Edit, Glob, Grep
from .bash import Bash, BashOutput, KillShell
from .git import Git
from .web import WebSearch, WebFetch
from .todo import TodoWrite


def get_default_registry() -> ToolRegistry:
    """Create and populate the default tool registry.

    Returns:
        ToolRegistry with all standard tools
    """
    registry = ToolRegistry()

    # File operations
    registry.register(Read())
    registry.register(Write())
    registry.register(Edit())
    registry.register(Glob())
    registry.register(Grep())

    # Bash execution
    bash_tool = Bash()
    registry.register(bash_tool)
    registry.register(BashOutput(bash_tool))
    registry.register(KillShell(bash_tool))

    # Git operations
    registry.register(Git())

    # Web tools
    registry.register(WebSearch())
    registry.register(WebFetch())

    # Task management
    registry.register(TodoWrite())

    return registry
