"""Base classes for the tool system."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """A parameter for a tool."""
    type: str
    description: str
    enum: Optional[List[str]] = None
    items: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None
    default: Optional[Any] = None


class ToolResult(BaseModel):
    """Result of a tool execution."""
    success: bool
    output: str
    error: Optional[str] = None


class Tool(ABC):
    """Base class for all tools."""

    def __init__(self):
        """Initialize the tool."""
        self.name = self.__class__.__name__

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult containing success status and output
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool.

        Returns:
            OpenAI-compatible function definition
        """
        pass

    def to_function_definition(self) -> Dict[str, Any]:
        """Convert to Z.ai function calling format.

        Returns:
            Function definition dict
        """
        return {
            "type": "function",
            "function": self.get_schema(),
        }


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool.

        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """Unregister a tool.

        Args:
            name: Tool name

        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_all(self) -> Dict[str, Tool]:
        """Get all registered tools.

        Returns:
            Dictionary of tool name to tool instance
        """
        return self._tools.copy()

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get function definitions for all tools.

        Returns:
            List of function definitions for Z.ai API
        """
        return [tool.to_function_definition() for tool in self._tools.values()]

    def execute(self, name: str, arguments: str) -> ToolResult:
        """Execute a tool by name with JSON arguments.

        Args:
            name: Tool name
            arguments: JSON string of arguments

        Returns:
            ToolResult
        """
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{name}' not found",
            )

        try:
            # Parse arguments
            args = json.loads(arguments) if arguments else {}

            # Execute tool
            return tool.execute(**args)
        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid JSON arguments: {e}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool execution failed: {e}",
            )
