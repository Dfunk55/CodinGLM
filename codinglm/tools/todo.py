"""TodoWrite tool for task management."""

from typing import Any, Dict, List, Literal
from pydantic import BaseModel
from .base import Tool, ToolResult


class TodoItem(BaseModel):
    """A todo item."""
    content: str
    status: Literal["pending", "in_progress", "completed"]
    activeForm: str


class TodoWrite(Tool):
    """Manage a todo list for tracking tasks."""

    def __init__(self):
        """Initialize TodoWrite tool."""
        super().__init__()
        self.todos: List[TodoItem] = []

    def execute(self, todos: List[Dict[str, str]]) -> ToolResult:
        """Update the todo list.

        Args:
            todos: List of todo items with content, status, and activeForm

        Returns:
            ToolResult
        """
        try:
            # Parse and validate todos
            self.todos = [TodoItem(**todo) for todo in todos]

            # Format output
            output_lines = ["Todo list updated:", ""]
            for i, todo in enumerate(self.todos, 1):
                status_icon = {
                    "pending": "⭘",
                    "in_progress": "→",
                    "completed": "✓",
                }[todo.status]
                output_lines.append(f"{i}. [{status_icon}] {todo.content}")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to update todos: {e}",
            )

    def get_current_todos(self) -> List[TodoItem]:
        """Get current todo list."""
        return self.todos.copy()

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for TodoWrite tool."""
        return {
            "name": "TodoWrite",
            "description": "Create and manage a structured task list for tracking progress",
            "parameters": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "description": "The updated todo list",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "The imperative form of the task (e.g., 'Run tests')",
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                    "description": "Task status",
                                },
                                "activeForm": {
                                    "type": "string",
                                    "description": "Present continuous form (e.g., 'Running tests')",
                                },
                            },
                            "required": ["content", "status", "activeForm"],
                        },
                    },
                },
                "required": ["todos"],
            },
        }
