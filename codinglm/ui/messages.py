"""Reusable UI text snippets."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple


def build_welcome_markdown(model: str, cwd: Path) -> str:
    return f"""# CodinGLM

Powered by Z.ai's {model}

Working directory: {cwd}

Type your request or use commands:
- /help - Show help
- /clear - Clear history
- /compact - Compress context
- /exit - Exit
"""


def build_help_markdown() -> str:
    return """# Available Commands

- `/help` - Show this help message
- `/clear` - Clear conversation history
- `/compact` - Manually trigger context compression
- `/metrics` - Display compression metrics and savings totals
- `/mcp list` - Show available MCP servers
- `/mcp enable <name>` - Enable an MCP server
- `/mcp disable <name>` - Disable an MCP server
- `/mcp status` - Show MCP server status
- `/permissions` - Show tool permissions
- `/model <name>` - Switch to another available model
- `/models` - Interactive model selector (arrow keys + Enter)
- `/tools` - Show detailed tool reference
- `/toolout [index]` - Show the full output for the most recent tool call
- `/exit` or `/quit` - Exit CodinGLM

## Available Tools

File Operations:
- Read, Write, Edit - File manipulation
- Glob, Grep - File search and content search

Execution:
- Bash - Execute shell commands
- Git - Git operations

**Tip:** Press `Esc` during streaming to interrupt the current response.

Web:
- WebFetch - Fetch web content

Task Management:
- TodoWrite - Track tasks
- Task - Spawn sub-agents for complex tasks

MCP Servers:
- Use `/mcp list` to see available servers
- Enable servers on-demand to save context
"""


def build_models_markdown(model_entries: Iterable[Tuple[str, str]]) -> str:
    lines = ["# Available Models", ""]
    for name, desc in model_entries:
        lines.append(f"- `{name}` - {desc}")
    lines.append("")
    lines.append("Use `/model <name>` or `/models` to switch models.")
    return "\n".join(lines)
