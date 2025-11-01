"""Task agent system for spawning sub-agents."""

from typing import Any, Dict, List, Optional
from ..api.client import GLMClient
from ..api.models import Message
from .base import Tool, ToolResult, ToolRegistry


class Task(Tool):
    """Launch sub-agents to handle complex tasks."""

    def __init__(self, client: GLMClient, registry: ToolRegistry):
        """Initialize Task tool.

        Args:
            client: GLM API client
            registry: Tool registry for sub-agent
        """
        super().__init__()
        self.client = client
        self.registry = registry

    def execute(
        self,
        description: str,
        prompt: str,
        subagent_type: str = "general-purpose",
    ) -> ToolResult:
        """Launch a sub-agent to handle a task.

        Args:
            description: Short description of the task
            prompt: Detailed task instructions for the agent
            subagent_type: Type of agent (general-purpose, Explore, etc.)

        Returns:
            ToolResult with agent's final response
        """
        try:
            # Create system prompt for sub-agent
            system_prompt = self._get_system_prompt(subagent_type)

            # Initialize conversation
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=prompt),
            ]

            # Run agent loop (simplified - no tool calling for now)
            max_iterations = 10
            for _ in range(max_iterations):
                # Get response from model
                response = self.client.chat(
                    messages=messages,
                    tools=self.registry.get_function_definitions(),
                    stream=False,
                )

                # Check if we have tool calls
                if isinstance(response, list):
                    # Execute tool calls
                    tool_results = []
                    for tool_call in response:
                        result = self.registry.execute(
                            tool_call.function["name"],
                            tool_call.function["arguments"],
                        )
                        tool_results.append(
                            Message(
                                role="tool",
                                content=result.output if result.success else f"Error: {result.error}",
                                tool_call_id=tool_call.id,
                            )
                        )

                    # Add assistant message with tool calls
                    messages.append(
                        Message(
                            role="assistant",
                            tool_calls=[
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": tc.function,
                                }
                                for tc in response
                            ],
                        )
                    )

                    # Add tool results
                    messages.extend(tool_results)

                else:
                    # Text response - agent is done
                    return ToolResult(
                        success=True,
                        output=f"Task: {description}\n\nResult:\n{response}",
                    )

            return ToolResult(
                success=False,
                output="",
                error="Agent exceeded maximum iterations",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Agent failed: {e}",
            )

    def _get_system_prompt(self, subagent_type: str) -> str:
        """Get system prompt for sub-agent type.

        Args:
            subagent_type: Type of agent

        Returns:
            System prompt string
        """
        if subagent_type == "Explore":
            return """You are a specialized code exploration agent. Your task is to:
- Quickly find files using Glob patterns
- Search code using Grep
- Read relevant files
- Answer questions about the codebase structure

Be thorough but efficient. Provide clear, concise answers."""

        # Default general-purpose agent
        return """You are a helpful coding assistant. You have access to various tools for:
- Reading and writing files
- Searching code
- Running commands
- Git operations

Use the tools available to complete the task autonomously. When done, provide a final summary."""

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Task tool."""
        return {
            "name": "Task",
            "description": "Launch a sub-agent to handle complex, multi-step tasks autonomously",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The detailed task for the agent to perform",
                    },
                    "subagent_type": {
                        "type": "string",
                        "description": "The type of specialized agent to use",
                        "enum": ["general-purpose", "Explore"],
                    },
                },
                "required": ["description", "prompt", "subagent_type"],
            },
        }
