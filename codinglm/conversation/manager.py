"""Conversation manager with history and tool execution."""

from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Optional

from rich.console import Console

from ..api.client import GLMClient
from ..api.models import Message, ToolCall, ToolResult as APIToolResult
from ..config import Config, ContextCompressionConfig
from ..logging import DebugEventLogger, TranscriptConsole
from ..mcp import MCPClientManager
from ..tools.base import ToolRegistry, ToolResult
from ..tools.history import ToolHistory, ToolHistoryEntry
from ..tools.task import Task
from ..ui.live_markdown import LiveMarkdownStream
from .compression import ContextCompressor, DISPLAY_TRUNCATE_LENGTH

if TYPE_CHECKING:
    from ..ui.renderer import MarkdownRenderer
    from ..ui.status import TurnStatus


class ConversationManager:
    """Manages conversation state and tool execution."""

    def __init__(
        self,
        client: GLMClient,
        registry: ToolRegistry,
        console: Console,
        compression_config: Optional[ContextCompressionConfig] = None,
        summarize_override: Optional[Callable[[List[Message]], str]] = None,
        mcp_config: Optional[Config] = None,
        max_tool_iterations: Optional[int] = None,
        debug: bool = False,
        debug_logger: Optional[DebugEventLogger] = None,
    ):
        """Initialize conversation manager.

        Args:
            client: GLM API client
            registry: Tool registry
            console: Rich console for output
            compression_config: Context compression configuration
            summarize_override: Optional override for summarization
            mcp_config: Full config including MCP servers
            max_tool_iterations: Optional cap on sequential tool executions (None for unlimited)
            debug: Enable verbose debug logging
        """
        self.client = client
        self.registry = registry
        self.console = console
        self.debug = debug
        self.debug_logger = debug_logger
        self.messages: List[Message] = []
        self.tool_history = ToolHistory()
        self.compressor = ContextCompressor(
            client=client,
            console=console,
            config=compression_config,
            summarize_override=summarize_override,
        )

        # Initialize MCP manager
        self.mcp_manager = MCPClientManager()

        # Register configured MCP servers
        if mcp_config and mcp_config.mcpServers:
            for name, server_config in mcp_config.mcpServers.items():
                self.mcp_manager.register_server(name, server_config)

        # Configure tool execution iteration limit
        if max_tool_iterations is not None:
            self.max_tool_iterations = max_tool_iterations
        elif mcp_config and mcp_config.tools.maxToolIterations is not None:
            self.max_tool_iterations = mcp_config.tools.maxToolIterations
        else:
            self.max_tool_iterations = None

        # Add Task tool (needs client and registry)
        task_tool = Task(client, registry)
        self.registry.register(task_tool)

        # Add system message
        self._initialize_system_message()

    def _initialize_system_message(self) -> None:
        """Add system message to conversation."""
        base_prompt = """You are CodinGLM, a helpful AI coding assistant powered by GLM-4.

You have access to Claude Code compatible tools. When you need to inspect files, run commands, or manage tasks, call the appropriate tool with the required parameters."""

        tool_primer = self._build_tool_primer()

        # Add context compression explanation if enabled
        context_info = ""
        if self.compressor.config.enabled:
            context_info = f"""
## Context Management

This conversation has automatic context compression enabled to manage token limits:
- Maximum context: ~{self.compressor.config.maxContextTokens:,} tokens
- Target after compression: ~{self.compressor.config.targetContextTokens:,} tokens
- Recent messages preserved: {self.compressor.config.preserveRecentMessages}

When the conversation exceeds the maximum, older messages are automatically summarized and replaced with a compression summary. You'll see these as assistant messages with metadata like "[context compression #N | ...]".

When you encounter a compression summary:
- Trust the summary content as accurate history
- Do NOT ask the user to repeat information from compressed messages
- Reference summary details naturally when relevant
- Continue the conversation as if the original messages occurred

The system handles compression automatically - you don't need to manage it."""

        guidelines = """Always:
1. Prefer tool calls over hallucinating results.
2. Provide clear descriptions before destructive commands.
3. Verify changes by reading relevant files or running tests.
4. Keep explanations concise and actionable.
5. When you see context compression summaries, treat them as authoritative history and avoid asking users to repeat that information."""

        system_prompt_parts = [base_prompt]
        if tool_primer:
            system_prompt_parts.append(tool_primer)
        if context_info:
            system_prompt_parts.append(context_info)
        system_prompt_parts.append(guidelines)

        system_prompt = "\n\n".join(system_prompt_parts)

        self.messages.append(Message(role="system", content=system_prompt))

    def _build_tool_primer(self) -> str:
        """Generate a primer describing the registered tools."""
        tools = self.registry.get_all()
        if not tools:
            return ""

        lines: List[str] = ["Tool Reference:"]
        for name in sorted(tools.keys()):
            tool = tools[name]
            schema = tool.get_schema()
            description = schema.get("description", "(no description)")
            parameters = schema.get("parameters", {})
            props = parameters.get("properties", {}) if isinstance(parameters, dict) else {}
            required = set(parameters.get("required", [])) if isinstance(parameters, dict) else set()

            lines.append(f"- {name}: {description}")
            if props:
                for param_name, param_schema in props.items():
                    if not isinstance(param_schema, dict):
                        continue
                    param_desc = param_schema.get("description", "").strip()
                    status = "required" if param_name in required else "optional"
                    if param_desc:
                        lines.append(f"  • {param_name} ({status}) – {param_desc}")
                    else:
                        lines.append(f"  • {param_name} ({status})")

        return "\n".join(lines)

    def _get_all_tools(self) -> List:
        """Get all available tool definitions (registry + MCP).

        Returns:
            List of tool function definitions
        """
        # Get tools from registry
        tools = self.registry.get_function_definitions()

        # Add MCP tools
        mcp_tools = self.mcp_manager.get_all_tools()
        for mcp_tool in mcp_tools:
            # Convert MCP tool format to function definition format
            tools.append({
                "type": "function",
                "function": {
                    "name": mcp_tool["name"],
                    "description": mcp_tool["description"],
                    "parameters": mcp_tool["parameters"],
                }
            })

        return tools

    def add_user_message(self, content: str) -> None:
        """Add a user message to conversation.

        Args:
            content: User message content
        """
        self.messages.append(Message(role="user", content=content))
        self._maybe_compress_context(trigger="user")

    def run_turn(
        self,
        stream: bool = True,
        should_stop: Optional[Callable[[], bool]] = None,
        status: Optional["TurnStatus"] = None,
        renderer: Optional["MarkdownRenderer"] = None,
    ) -> Optional[str]:
        """Run a conversation turn with tool execution.

        Args:
            stream: Whether to stream the response
            should_stop: Optional interrupt callback
            status: Optional status reporter for progress updates
            renderer: Optional renderer for final assistant output

        Returns:
            Final assistant response or None if tools were called
        """
        iteration = 0
        while True:
            if self.debug:
                self._debug(
                    f"Turn iteration {iteration + 1} starting "
                    f"(messages={len(self.messages)}, max_iter={self.max_tool_iterations})",
                    {
                        "iteration": iteration + 1,
                        "max_tool_iterations": self.max_tool_iterations,
                        "streaming": stream,
                    },
                )
            if (
                self.max_tool_iterations is not None
                and iteration >= self.max_tool_iterations
            ):
                self.console.print("[yellow]Warning: Maximum tool iterations reached[/yellow]")
                self._debug(
                    "Stopping conversation turn after reaching max_tool_iterations "
                    f"({self.max_tool_iterations})",
                    {"iteration": iteration, "max_tool_iterations": self.max_tool_iterations},
                )
                return None

            # Get model response
            if stream:
                response = self._handle_streaming_response(
                    should_stop=should_stop,
                    status=status,
                    renderer=renderer,
                )
            else:
                response = self.client.chat(
                    messages=self.messages,
                    tools=self._get_all_tools(),
                    stream=False,
                )

            # Check if we have tool calls
            if isinstance(response, list):
                if self.debug:
                    self._debug(
                        f"Model returned {len(response)} pending tool call(s)",
                        {"pending_tool_calls": len(response)},
                    )
                # Execute tools
                self._execute_tools(response, status=status)
            else:
                # Text response - we're done
                if self.debug:
                    self._debug(
                        "Model produced a final assistant message; ending turn",
                        {"response_length": len(response) if isinstance(response, str) else None},
                    )
                self.messages.append(Message(role="assistant", content=response))
                self._maybe_compress_context(trigger="assistant")
                if not stream and isinstance(response, str):
                    if renderer:
                        renderer.render_assistant_markdown(response)
                    else:
                        self.console.print(response)
                return response

            iteration += 1

    def _handle_streaming_response(
        self,
        should_stop: Optional[Callable[[], bool]] = None,
        status: Optional["TurnStatus"] = None,
        renderer: Optional["MarkdownRenderer"] = None,
    ) -> str | List[ToolCall]:
        """Handle streaming response from API.

        Returns:
            Either accumulated text or list of tool calls
        """
        if self.debug:
            self._debug(
                "Streaming response initiated",
                {"messages": len(self.messages), "tools_available": len(self._get_all_tools())},
            )
        response_text = ""
        tool_calls: List[ToolCall] = []
        interrupted = False
        first_token = True
        status_message = "Streaming response… (Esc to interrupt)"

        stream = self.client.chat(
            messages=self.messages,
            tools=self._get_all_tools(),
            stream=True,
        )

        if status:
            status.update(status_message)
            status.stop()
            self.console.print(f"[dim]{status_message}[/dim]")

        live_stream = LiveMarkdownStream(self.console)
        with live_stream:
            for chunk in stream:
                if chunk.delta:
                    if first_token:
                        first_token = False
                    live_stream.append(chunk.delta)
                    response_text += chunk.delta

                if chunk.tool_calls:
                    tool_calls.extend(chunk.tool_calls)

                if chunk.finish_reason:
                    break

                if should_stop and should_stop():
                    if self.debug:
                        self._debug(
                            "Streaming interrupted by stop callback",
                            {"response_text_length": len(response_text)},
                        )
                    interrupted = True
                    break

        if tool_calls and not interrupted:
            if status:
                status.update("Tool execution requested…")
            if self.debug:
                self._debug(
                    f"Streaming produced {len(tool_calls)} tool call(s)",
                    {"tool_calls": len(tool_calls)},
                )
            return tool_calls

        if tool_calls and interrupted and response_text:
            if self.debug:
                self._debug(
                    "Streaming interrupted with partial response; returning accumulated text",
                    {"response_text_length": len(response_text), "tool_calls": len(tool_calls)},
                )
            if renderer and response_text:
                renderer.render_assistant_markdown(response_text)
            elif response_text:
                self.console.print(response_text)
            return response_text

        if response_text:
            if self.debug:
                self._debug(
                    "Streaming produced text response without tool calls",
                    {"response_text_length": len(response_text)},
                )
            if renderer:
                renderer.render_assistant_markdown(response_text)
            else:
                self.console.print(response_text)

        return response_text

    def _execute_tools(
        self,
        tool_calls: List[ToolCall],
        status: Optional["TurnStatus"] = None,
    ) -> None:
        """Execute tool calls and add results to conversation.

        Args:
            tool_calls: List of tool calls from model
        """
        # Add assistant message with tool calls
        self.messages.append(
            Message(
                role="assistant",
                tool_calls=[
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": tc.function,
                    }
                    for tc in tool_calls
                ],
            )
        )

        # Execute each tool
        for tool_call in tool_calls:
            tool_name = tool_call.function["name"]
            tool_args = tool_call.function["arguments"]

            self.console.print(f"\n[cyan]→ Executing: {tool_name}[/cyan]")
            if status:
                status.update(f"Running tool {tool_name}…")
            display_args = tool_args if isinstance(tool_args, str) else str(tool_args)
            if isinstance(display_args, str) and len(display_args) > 200:
                display_args = f"{display_args[:200]}..."

            self._emit_debug_event(
                "tool_execution_start",
                f"Executing tool '{tool_name}'",
                {
                    "tool_name": tool_name,
                    "tool_call_id": tool_call.id,
                    "arguments_preview": display_args,
                },
            )

            # Check if this is an MCP tool
            if tool_name.startswith("mcp::"):
                # Execute MCP tool (async)
                import asyncio
                import json
                try:
                    if self.debug:
                        self._debug(
                            f"Dispatching MCP tool '{tool_name}'",
                            {"tool_name": tool_name, "tool_call_id": tool_call.id},
                        )
                    args_dict = json.loads(tool_args) if isinstance(tool_args, str) else tool_args
                    mcp_result = asyncio.run(self.mcp_manager.call_tool(tool_name, args_dict))
                    # Convert MCP result to ToolResult format
                    from ..tools.base import ToolResult
                    # MCP returns a dict with 'content' array
                    content = mcp_result.get("content", [])
                    output = ""
                    for item in content:
                        if item.get("type") == "text":
                            output += item.get("text", "")
                    result = ToolResult(success=True, output=output)
                except Exception as e:
                    from ..tools.base import ToolResult
                    if self.debug:
                        self._debug(
                            f"MCP tool '{tool_name}' raised exception: {e}",
                            {"tool_name": tool_name, "tool_call_id": tool_call.id, "error": str(e)},
                        )
                    result = ToolResult(success=False, output="", error=str(e))
            else:
                # Execute regular tool
                if self.debug:
                    self._debug(
                        f"Executing tool '{tool_name}' with args={display_args}",
                        {
                            "tool_name": tool_name,
                            "tool_call_id": tool_call.id,
                            "arguments_preview": display_args,
                        },
                    )
                result = self.registry.execute(tool_name, tool_args)

            # Display result
            truncated = False
            output_for_display = result.output or ""

            if result.success:
                self.console.print("[green]✓[/green] Tool completed")
                if output_for_display:
                    truncated = len(output_for_display) > DISPLAY_TRUNCATE_LENGTH
                    self.console.print(output_for_display[:DISPLAY_TRUNCATE_LENGTH])
                if self.debug:
                    self._debug(
                        f"Tool '{tool_name}' completed successfully",
                        {
                            "tool_name": tool_name,
                            "tool_call_id": tool_call.id,
                            "output_preview": result.output[:200] if result.output else "",
                        },
                    )
                self._emit_debug_event(
                    "tool_execution_success",
                    f"Tool '{tool_name}' completed successfully",
                    {
                        "tool_name": tool_name,
                        "tool_call_id": tool_call.id,
                        "output_preview": result.output[:200] if result.output else "",
                    },
                )
            else:
                self.console.print(f"[red]✗[/red] Error: {result.error}")
                if self.debug:
                    self._debug(
                        f"Tool '{tool_name}' failed with error: {result.error}",
                        {
                            "tool_name": tool_name,
                            "tool_call_id": tool_call.id,
                            "error": result.error,
                        },
                    )
                self._emit_debug_event(
                    "tool_execution_error",
                    f"Tool '{tool_name}' failed",
                    {
                        "tool_name": tool_name,
                        "tool_call_id": tool_call.id,
                        "error": result.error,
                    },
                )

            # Add result to conversation
            self.messages.append(
                Message(
                    role="tool",
                    content=result.output if result.success else f"Error: {result.error}",
                    tool_call_id=tool_call.id,
                )
            )
            self._maybe_compress_context(trigger=tool_name)

            self.tool_history.add(
                ToolHistoryEntry(
                    name=tool_name,
                    call_id=tool_call.id,
                    success=result.success,
                    output=result.output if result.output else (result.error or ""),
                )
            )
            if truncated:
                history_index = len(self.tool_history)
                self.console.print(
                    f"[dim]… output truncated. Use /toolout {history_index} to view the full result.[/dim]"
                )

    def clear_history(self) -> None:
        """Clear conversation history (keeping system message)."""
        system_message = self.messages[0]
        self.messages = [system_message]
        self.compressor.reset()
        self.console.print("[yellow]Conversation history cleared[/yellow]")
        self.tool_history.clear()

    def get_tool_history(self) -> ToolHistory:
        """Return the stored tool execution history."""
        return self.tool_history

    def _maybe_compress_context(self, trigger: str) -> None:
        """Run context compression if the conversation is too large."""
        # Avoid compressing if only the system prompt is present.
        if len(self.messages) <= 1:
            return
        self.compressor.maybe_compress(self.messages, trigger=trigger)

    def _emit_debug_event(
        self,
        event: str,
        message: str,
        extra: Optional[Dict[str, object]] = None,
    ) -> None:
        """Record structured debug events."""
        if not self.debug_logger:
            return

        payload: Dict[str, object] = {"message_count": len(self.messages)}
        if extra:
            payload.update(extra)
        self.debug_logger.emit(event, message, payload)

    def _debug(self, message: str, extra: Optional[Dict[str, object]] = None) -> None:
        """Emit a debug message when debug mode is active."""
        if self.debug:
            if isinstance(self.console, TranscriptConsole):
                self.console.log_transcript_only(f"DEBUG: {message}")
            else:
                self.console.print(f"[dim]DEBUG: {message}[/dim]")
        self._emit_debug_event("conversation_debug", message, extra)
