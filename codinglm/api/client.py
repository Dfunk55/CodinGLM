"""Z.ai Anthropomorphic API client with streaming and tool support."""

from __future__ import annotations

import json
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Dict, Iterator, List, Optional, Union

import httpx
from rich.console import Console

from .models import Message, StreamChunk, ToolCall, ToolDefinition, ToolResult


@dataclass
class _ToolUseState:
    """Track in-flight tool use blocks during streaming."""

    id: str
    name: str
    input_dict: Dict[str, Any]
    input_buffer: str = ""

    def append_partial(self, fragment: str) -> None:
        """Append a partial JSON fragment to the buffer."""
        self.input_buffer += fragment

    def arguments_json(self) -> str:
        """Return the final JSON string representing tool arguments."""
        if self.input_buffer:
            candidate = self.input_buffer
            try:
                json.loads(candidate)
            except json.JSONDecodeError:
                if self.input_dict:
                    return json.dumps(self.input_dict, ensure_ascii=False)
                return candidate
            return candidate

        if self.input_dict:
            return json.dumps(self.input_dict, ensure_ascii=False)

        return "{}"


class GLMClient:
    """Wrapper around Z.ai Anthropomorphic API with Claude-compatible semantics."""

    ANTHROPIC_VERSION = "2023-06-01"
    DEFAULT_BASE_URL = "https://api.z.ai/api/anthropic"
    DEFAULT_TIMEOUT_SECONDS = 600

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4.6",
        temperature: float = 0.7,
        max_tokens: int = 8192,
        base_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        console: Optional[Console] = None,
    ):
        """Initialize the GLM client.

        Args:
            api_key: Z.ai API key (GLM Coding Plan)
            model: Model name (e.g., glm-4.6, glm-4.5-air, glm-4-flash)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            base_url: Override API base URL
            timeout_ms: Request timeout in milliseconds
            console: Rich console for logging
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        timeout_seconds = (
            timeout_ms / 1000 if timeout_ms is not None else self.DEFAULT_TIMEOUT_SECONDS
        )
        self.timeout = timeout_seconds
        self.console = console or Console()

    # --------------------------------------------------------------------- #
    # Public interface
    # --------------------------------------------------------------------- #
    def chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        stream: bool = False,
    ) -> Union[str, Iterator[StreamChunk], List[ToolCall]]:
        """Send a chat request to the GLM coding plan API.

        Args:
            messages: Conversation history
            tools: Available tools/functions
            stream: Whether to stream the response

        Returns:
            If stream=False and no tool calls: str (response content)
            If stream=False and tool calls: List[ToolCall]
            If stream=True: Iterator[StreamChunk]
        """
        payload = self._build_payload(messages, tools)

        if stream:
            return self._stream_messages(payload)

        response = self._post_messages(payload)
        return self._handle_response(response)

    def create_tool_result_message(self, result: ToolResult) -> Message:
        """Create a message from a tool result."""
        return Message(
            role="tool",
            content=result.content,
            tool_call_id=result.tool_call_id,
        )

    # --------------------------------------------------------------------- #
    # Request/response plumbing
    # --------------------------------------------------------------------- #
    def _post_messages(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a non-streaming messages request."""
        headers = self._build_headers()
        url = f"{self.base_url}/v1/messages"

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(self._format_api_error(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Network error: {exc}") from exc

        return response.json()

    def _stream_messages(self, payload: Dict[str, Any]) -> Iterator[StreamChunk]:
        """Stream response chunks as they arrive."""
        headers = self._build_headers()
        url = f"{self.base_url}/v1/messages"
        payload = dict(payload)
        payload["stream"] = True

        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    yield from self._parse_event_stream(response)
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(self._format_api_error(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Network error: {exc}") from exc

    # --------------------------------------------------------------------- #
    # Payload helpers
    # --------------------------------------------------------------------- #
    def _build_payload(
        self,
        messages: List[Message],
        tools: Optional[List[Union[ToolDefinition, Dict[str, Any]]]],
    ) -> Dict[str, Any]:
        """Convert internal messages/tools to Anthropomorphic payload."""
        system_prompt, anthropic_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": anthropic_messages,
        }

        if system_prompt:
            payload["system"] = system_prompt

        if tools:
            payload["tools"] = [self._tool_to_anthropic(tool) for tool in tools]

        return payload

    def _convert_messages(self, messages: List[Message]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Convert CodinGLM messages to Anthropomorphic format."""
        system_prompts: List[str] = []
        converted: List[Dict[str, Any]] = []

        for message in messages:
            if message.role == "system":
                if message.content:
                    system_prompts.append(message.content)
                continue

            if message.role == "user":
                content = [{"type": "text", "text": message.content or ""}]
                converted.append({"role": "user", "content": content})
                continue

            if message.role == "assistant":
                content_blocks: List[Dict[str, Any]] = []
                if message.content:
                    content_blocks.append({"type": "text", "text": message.content})

                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        function = tool_call.get("function", {})
                        name = function.get("name", "")
                        arguments = function.get("arguments", "{}")
                        parsed_args = self._safe_json_loads(arguments)
                        content_blocks.append(
                            {
                                "type": "tool_use",
                                "id": tool_call.get("id", ""),
                                "name": name,
                                "input": parsed_args,
                            }
                        )

                # Anthropomorphic API requires at least one block
                if not content_blocks:
                    content_blocks.append({"type": "text", "text": ""})

                converted.append({"role": "assistant", "content": content_blocks})
                continue

            if message.role == "tool":
                if message.content is None:
                    continue
                content_blocks = [
                    {
                        "type": "tool_result",
                        "tool_use_id": message.tool_call_id or "",
                        "content": message.content,
                    }
                ]
                converted.append({"role": "user", "content": content_blocks})
                continue

            # Fallback: treat unknown roles as plain text.
            if message.content:
                converted.append({"role": "user", "content": [{"type": "text", "text": message.content}]})

        system_prompt = "\n\n".join(system_prompts) if system_prompts else None
        return system_prompt, converted

    def _tool_to_anthropic(self, tool: Union[ToolDefinition, Dict[str, Any]]) -> Dict[str, Any]:
        """Translate OpenAI-style tool definition to Anthropomorphic format."""
        if isinstance(tool, ToolDefinition):
            function = tool.function
        else:
            function = tool.get("function", {})

        parameters = function.get("parameters")
        if parameters and not isinstance(parameters, dict):
            parameters = self._safe_json_loads(parameters)

        return {
            "type": "tool",
            "name": function.get("name", ""),
            "description": function.get("description", ""),
            "input_schema": parameters or {"type": "object", "properties": {}},
        }

    # --------------------------------------------------------------------- #
    # Response handling
    # --------------------------------------------------------------------- #
    def _handle_response(self, response: Dict[str, Any]) -> Union[str, List[ToolCall]]:
        """Handle non-streaming response."""
        tool_calls: List[ToolCall] = []
        text_parts: List[str] = []

        for block in response.get("content", []):
            block_type = block.get("type")
            if block_type == "text":
                text_parts.append(block.get("text", ""))
            elif block_type == "tool_use":
                arguments = json.dumps(block.get("input", {}), ensure_ascii=False)
                tool_calls.append(
                    ToolCall(
                        id=block.get("id", ""),
                        type="function",
                        function={
                            "name": block.get("name", ""),
                            "arguments": arguments,
                        },
                    )
                )

        if tool_calls:
            return tool_calls

        return "".join(text_parts)

    def _parse_event_stream(self, response: httpx.Response) -> Iterator[StreamChunk]:
        """Parse server-sent events into StreamChunk objects."""
        current_event: Optional[str] = None
        tool_states: Dict[int, _ToolUseState] = {}

        for raw_line in response.iter_lines():
            if not raw_line:
                continue

            line = raw_line.decode("utf-8") if isinstance(raw_line, (bytes, bytearray)) else raw_line
            if line.startswith("event:"):
                current_event = line[len("event:") :].strip()
                continue

            if not line.startswith("data:"):
                continue

            if current_event is None:
                continue

            if line.strip() == "data: [DONE]":
                chunk = StreamChunk(finish_reason="stop")
                yield chunk
                break

            data = line[len("data:") :].strip()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue

            # Handle API-side error events
            if current_event == "error":
                message = payload.get("error", {}).get("message")
                raise RuntimeError(message or "Unknown streaming error")

            chunk = StreamChunk()

            if current_event == "content_block_delta":
                delta = payload.get("delta", {})
                delta_type = delta.get("type")
                if delta_type == "text_delta":
                    chunk.delta = delta.get("text", "")
                elif delta_type == "input_json_delta":
                    index = payload.get("index", 0)
                    tool_state = tool_states.get(index)
                    if tool_state:
                        fragment = delta.get("partial_json", "")
                        tool_state.append_partial(fragment)

            elif current_event == "content_block_start":
                block = payload.get("content_block", {})
                if block.get("type") == "tool_use":
                    index = payload.get("index", 0)
                    initial_input = block.get("input", {})
                    input_dict: Dict[str, Any] = {}
                    input_buffer = ""

                    if isinstance(initial_input, dict):
                        input_dict = initial_input
                    elif isinstance(initial_input, str):
                        input_buffer = initial_input

                    tool_state = _ToolUseState(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        input_dict=input_dict,
                        input_buffer=input_buffer,
                    )
                    tool_states[index] = tool_state

            elif current_event == "content_block_stop":
                index = payload.get("index", 0)
                tool_state = tool_states.pop(index, None)
                if tool_state:
                    arguments = tool_state.arguments_json()
                    chunk.tool_calls = [
                        ToolCall(
                            id=tool_state.id,
                            type="function",
                            function={
                                "name": tool_state.name,
                                "arguments": arguments,
                            },
                        )
                    ]

            elif current_event == "message_delta":
                delta = payload.get("delta", {})
                stop_reason = delta.get("stop_reason")
                if stop_reason:
                    chunk.finish_reason = stop_reason

            elif current_event == "message_stop":
                chunk.finish_reason = payload.get("stop_reason", "stop")

            # Only yield meaningful chunks
            if chunk.delta or chunk.tool_calls or chunk.finish_reason:
                yield chunk

    # --------------------------------------------------------------------- #
    # Utility helpers
    # --------------------------------------------------------------------- #
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        return {
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": self.ANTHROPIC_VERSION,
        }

    @staticmethod
    def _safe_json_loads(value: Any) -> Any:
        """Parse JSON value if possible, otherwise return original."""
        if isinstance(value, (dict, list)):
            return value
        if not isinstance(value, str):
            return value
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"__raw": value}

    @staticmethod
    def _format_api_error(response: httpx.Response) -> str:
        """Extract a readable message from API error responses."""
        try:
            data = response.json()
        except Exception:
            return f"API error: HTTP {response.status_code}"

        if isinstance(data, dict):
            error = data.get("error")
            if isinstance(error, dict):
                code = error.get("code")
                message = error.get("message")
                if code and message:
                    return f"API error ({code}): {message}"
                if message:
                    return f"API error: {message}"
        return f"API error: HTTP {response.status_code}"

    # --------------------------------------------------------------------- #
    # Context management (optional future use)
    # --------------------------------------------------------------------- #
    def __enter__(self) -> "GLMClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """No persistent resources to release (client created per call)."""
        return None
