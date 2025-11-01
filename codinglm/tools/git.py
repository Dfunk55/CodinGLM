"""Git operations and PR creation tools."""

import subprocess
from typing import Any, Dict, Optional

from .base import Tool, ToolResult


class Git(Tool):
    """Execute git commands."""

    def execute(self, command: str, description: Optional[str] = None) -> ToolResult:
        """Execute a git command.

        Args:
            command: Git command to execute
            description: Description of the command

        Returns:
            ToolResult with command output
        """
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            return ToolResult(
                success=result.returncode == 0,
                output=output.strip() if output else "Command completed",
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}",
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Git command timed out",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Git tool."""
        return {
            "name": "Git",
            "description": "Execute git commands for version control operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Git command to execute (without 'git' prefix)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what the command does",
                    },
                },
                "required": ["command"],
            },
        }
