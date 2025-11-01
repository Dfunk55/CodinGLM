"""Data models for API interactions."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in the conversation."""
    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ToolDefinition(BaseModel):
    """Definition of a tool/function."""
    type: Literal["function"] = "function"
    function: Dict[str, Any]


class ToolCall(BaseModel):
    """A tool call from the model."""
    id: str
    type: Literal["function"] = "function"
    function: Dict[str, Any]  # Contains 'name' and 'arguments' (JSON string)


class ToolResult(BaseModel):
    """Result of a tool execution."""
    tool_call_id: str
    content: str
    is_error: bool = False


class StreamChunk(BaseModel):
    """A chunk from a streaming response."""
    delta: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: Optional[str] = None
