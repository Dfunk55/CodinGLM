"""CLI application for CodinGLM."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from prompt_toolkit import PromptSession
try:
    from prompt_toolkit.shortcuts import radiolist_dialog
except Exception:  # pragma: no cover - dialog optional at runtime
    radiolist_dialog = None  # type: ignore[assignment]

from .api.client import GLMClient
from .config import Config
from .conversation.manager import ConversationManager
from .logging import DebugEventLogger, TranscriptConsole
from .tools.registry import get_default_registry
from .ui.interrupt import StreamInterruptWatcher
from .ui.messages import (
    build_help_markdown,
    build_models_markdown,
    build_welcome_markdown,
)
from .ui.prompt import PromptSessionFactory
from .ui.renderer import MarkdownRenderer
from .ui.status import TurnStatus


AVAILABLE_MODELS: Dict[str, str] = {
    "glm-4.6": "Flagship GLM Coding Plan model (recommended)",
    "glm-4.5-air": "Fast, cost-effective coding model",
    "glm-4-flash": "Ultra-fast responses for quick tasks",
}

COMMAND_DESCRIPTIONS: Dict[str, str] = {
    "/help": "Show help",
    "/clear": "Clear conversation history",
    "/compact": "Manually trigger context compression",
    "/metrics": "Display compression metrics",
    "/mcp": "Manage MCP servers",
    "/permissions": "Show tool permissions",
    "/model": "Switch model",
    "/models": "Interactive model selector",
    "/tools": "Show tool reference",
    "/toolout": "Show full output of the last tool call",
    "/exit": "Exit CodinGLM",
    "/quit": "Exit CodinGLM",
}


class CodinGLMCLI:
    """Main CLI application."""

    def __init__(
        self,
        config: Config,
        cwd: Path,
        debug: bool = True,
    ) -> None:
        self.config = config
        self.cwd = cwd
        self.debug = debug
        session_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_id = session_stamp

        transcript_path: Optional[Path] = None
        debug_events_path: Optional[Path] = None
        if self.debug:
            logs_dir = Path.home() / ".codinglm" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            transcript_path = logs_dir / f"session-{session_stamp}.log"
            debug_events_path = logs_dir / f"session-{session_stamp}.jsonl"

        self.console = TranscriptConsole(
            transcript_path=transcript_path,
            soft_wrap=True,
        )
        self.renderer = MarkdownRenderer(self.console)
        self.debug_log_path = transcript_path
        self.debug_logger = DebugEventLogger(debug_events_path) if debug_events_path else None

        if self.debug and transcript_path and isinstance(self.console, TranscriptConsole):
            self.console.log_transcript_only(f"Debug transcript active → {transcript_path}")
        if self.debug_logger and isinstance(self.console, TranscriptConsole):
            self.console.log_transcript_only(f"Structured debug events → {self.debug_logger.path}")
            self._emit_debug_event(
                "session_start",
                "CodinGLM session started",
                {"session_id": self.session_id, "cwd": str(self.cwd)},
            )

        try:
            api_key = config.get_api_key()
            self.client = GLMClient(
                api_key=api_key,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.maxTokens,
                base_url=config.apiBase,
                timeout_ms=config.apiTimeoutMs,
                console=self.console,
            )
        except ValueError as exc:
            self.console.print(f"[red]Configuration error: {exc}[/red]")
            raise SystemExit(1) from exc

        self.registry = get_default_registry()
        self.conversation = ConversationManager(
            client=self.client,
            registry=self.registry,
            console=self.console,
            compression_config=self.config.context.compression,
            mcp_config=self.config,
            max_tool_iterations=self.config.tools.maxToolIterations,
            debug=self.debug,
            debug_logger=self.debug_logger,
        )

        history_file = Path.home() / ".codinglm-history"
        prompt_factory = PromptSessionFactory(
            COMMAND_DESCRIPTIONS,
            str(history_file),
        )
        self.session: PromptSession = prompt_factory.build()
        self._command_triggers = {cmd.lower() for cmd in COMMAND_DESCRIPTIONS}
        self._shutdown_done = False

    def _emit_debug_event(
        self,
        event: str,
        message: str,
        extra: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if not self.debug_logger:
            return

        payload: Dict[str, Any] = {"session_id": self.session_id}
        if extra:
            payload.update(extra)
        self.debug_logger.emit(event, message, payload)

    def _shutdown(self) -> None:
        if self._shutdown_done:
            return

        self._shutdown_done = True
        self._emit_debug_event("session_end", "CodinGLM session shutting down")

        if isinstance(self.console, TranscriptConsole):
            self.console.close()
        elif hasattr(self.console, "close"):
            try:
                self.console.close()  # type: ignore[call-arg]
            except Exception:
                pass

        if self.debug_logger:
            try:
                self.debug_logger.close()
            except Exception:
                pass

    def run(self) -> None:
        self._print_welcome()

        try:
            while True:
                try:
                    user_input = self.session.prompt("\n> ")
                    if not user_input.strip():
                        continue

                    self._emit_debug_event(
                        "user_input",
                        "User submitted input",
                        {"content": user_input},
                    )

                    if self._is_slash_command(user_input):
                        self._handle_command(user_input)
                        continue

                    if isinstance(self.console, TranscriptConsole):
                        with self.console.capture() as capture:
                            self.renderer.render_user_message(user_input)
                        transcript_panel = capture.get()
                        if transcript_panel.strip():
                            self.console.log_transcript_only(transcript_panel.rstrip("\n"))
                    else:
                        self.renderer.render_user_message(user_input)
                    self.conversation.add_user_message(user_input)
                    self._emit_debug_event(
                        "conversation_turn",
                        "Conversation turn started",
                        {"message_count": len(self.conversation.messages)},
                    )

                    status = TurnStatus(self.console)
                    status.start("Contacting model…")
                    interrupt = StreamInterruptWatcher()
                    interrupt.start()
                    try:
                        self.conversation.run_turn(
                            stream=True,
                            should_stop=interrupt.should_stop,
                            status=status,
                            renderer=self.renderer,
                        )
                    finally:
                        status.stop()
                        if interrupt.stop():
                            self.console.print("[yellow]Response interrupted (Esc)[/yellow]")
                            self._emit_debug_event(
                                "stream_interrupt",
                                "User interrupted streaming output",
                            )
                        else:
                            self._emit_debug_event(
                                "conversation_turn_complete",
                                "Conversation turn completed",
                                {"message_count": len(self.conversation.messages)},
                            )

                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use /exit to quit[/yellow]")
                    self._emit_debug_event("keyboard_interrupt", "KeyboardInterrupt received")
                    continue
                except EOFError:
                    self._emit_debug_event("eof", "EOF received")
                    break
                except Exception as exc:
                    self._emit_debug_event(
                        "cli_error",
                        "CLI raised exception",
                        {"exception": repr(exc)},
                    )
                    if self.debug:
                        raise
                    self.renderer.render_error(str(exc))
        finally:
            self._shutdown()

        self._print_goodbye()

    def _handle_command(self, command: str) -> None:
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        self._emit_debug_event(
            "slash_command",
            "Slash command invoked",
            {"command": cmd, "args": args},
        )

        if cmd in {"/exit", "/quit"}:
            self._print_goodbye()
            self._shutdown()
            raise SystemExit(0)

        if cmd == "/clear":
            self.conversation.clear_history()
            return
        if cmd == "/compact":
            self._handle_compact_command()
            return
        if cmd == "/metrics":
            self._handle_metrics_command()
            return
        if cmd == "/help":
            self._print_help()
            return
        if cmd == "/permissions":
            self._print_permissions()
            return
        if cmd == "/models":
            self._print_models()
            return
        if cmd == "/model":
            self._handle_model_command(args.strip())
            return
        if cmd == "/tools":
            self._print_tools()
            return
        if cmd == "/toolout":
            self._print_tool_output(args.strip())
            return
        if cmd == "/mcp":
            self._handle_mcp_command(args.strip())
            return

        self.renderer.render_error(f"Unknown command: {command}")
        self.console.print("Type /help for available commands")

    def _handle_compact_command(self) -> None:
        from .utils.token_counter import estimate_messages_tokens

        tokens_before = estimate_messages_tokens(self.conversation.messages)
        messages_before = len(self.conversation.messages)

        self.conversation.compressor.maybe_compress(
            self.conversation.messages,
            trigger="manual",
        )

        tokens_after = estimate_messages_tokens(self.conversation.messages)
        messages_after = len(self.conversation.messages)

        if messages_before == messages_after:
            self.console.print(
                f"[yellow]No compression performed[/yellow]\n"
                f"Current: {tokens_after:,} tokens, {messages_after} messages\n"
                f"Limit: {self.conversation.compressor.config.maxContextTokens:,} tokens"
            )
        else:
            messages_removed = messages_before - messages_after
            tokens_saved = tokens_before - tokens_after
            reduction_pct = (tokens_saved / tokens_before * 100) if tokens_before > 0 else 0

            self.console.print(
                "[green]✓ Context compressed[/green]\n"
                f"Removed: {messages_removed} messages\n"
                f"Tokens: {tokens_before:,} → {tokens_after:,} "
                f"(saved {tokens_saved:,}, {reduction_pct:.1f}%)"
            )

        metrics = self.conversation.compressor.get_metrics()
        self._emit_debug_event(
            "compression_manual",
            "Manual compression executed",
            {
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "messages_before": messages_before,
                "messages_after": messages_after,
                "total_compressions": metrics.total_compressions,
            },
        )

    def _handle_metrics_command(self) -> None:
        metrics = self.conversation.compressor.get_metrics()
        ratio = metrics.get_compression_ratio()
        tokens_saved = metrics.get_tokens_saved()

        self.console.print("\n[bold]Compression Metrics[/bold]\n")
        self.console.print(
            f"Compressions: {metrics.total_compressions} | "
            f"Messages compressed: {metrics.total_messages_compressed}"
        )
        self.console.print(
            f"Tokens saved: {tokens_saved:,} ({ratio:.1%}) | "
            f"API calls: {metrics.api_calls_successful} | "
            f"Fallbacks: {metrics.fallback_summaries_used}"
        )
        self.console.print("")

        self._emit_debug_event(
            "metrics_report",
            "Compression metrics reported",
            {
                "total_compressions": metrics.total_compressions,
                "messages_compressed": metrics.total_messages_compressed,
                "tokens_saved": tokens_saved,
                "compression_ratio": ratio,
                "api_calls": metrics.api_calls_successful,
                "fallbacks": metrics.fallback_summaries_used,
            },
        )

    def _handle_mcp_command(self, args: str) -> None:
        import asyncio

        parts = args.split(maxsplit=1)
        if not parts or not parts[0]:
            self.console.print("[yellow]Usage: /mcp <list|enable|disable|status> [server-name][/yellow]")
            return

        subcmd = parts[0].lower()
        server_name = parts[1] if len(parts) > 1 else None

        if subcmd == "list":
            self._mcp_list()
        elif subcmd == "enable":
            if not server_name:
                self.console.print("[yellow]Usage: /mcp enable <server-name>[/yellow]")
                return
            asyncio.run(self._mcp_enable(server_name))
        elif subcmd == "disable":
            if not server_name:
                self.console.print("[yellow]Usage: /mcp disable <server-name>[/yellow]")
                return
            asyncio.run(self._mcp_disable(server_name))
        elif subcmd == "status":
            self._mcp_status()
        else:
            self.console.print(f"[yellow]Unknown MCP command: {subcmd}[/yellow]")
            self.console.print("Available commands: list, enable, disable, status")

    def _mcp_list(self) -> None:
        available = self.conversation.mcp_manager.get_available_servers()
        enabled = set(self.conversation.mcp_manager.get_enabled_servers())

        if not available:
            self.console.print("[yellow]No MCP servers configured[/yellow]")
            self.console.print("Add servers to .codinglm.json in the 'mcpServers' section")
            return

        self.console.print("\n[bold]Available MCP Servers:[/bold]\n")
        for name in available:
            status = "[x]" if name in enabled else "[ ]"
            state = "[green]ACTIVE[/green]" if name in enabled else ""
            self.console.print(f"  {status} {name} {state}")
        self.console.print()

    async def _mcp_enable(self, server_name: str) -> None:
        self.console.print(f"[cyan]Enabling MCP server: {server_name}[/cyan]")
        success = await self.conversation.mcp_manager.enable_server(server_name)

        if success:
            connection = self.conversation.mcp_manager.servers.get(server_name)
            if connection:
                tools = connection.tools
                self.console.print(f"[green]✓ Enabled {server_name} ({len(tools)} tools loaded)[/green]")
            else:
                self.console.print(f"[green]✓ Enabled {server_name}[/green]")
        else:
            self.console.print(f"[red]✗ Failed to enable {server_name}[/red]")

    async def _mcp_disable(self, server_name: str) -> None:
        self.console.print(f"[cyan]Disabling MCP server: {server_name}[/cyan]")
        success = await self.conversation.mcp_manager.disable_server(server_name)

        if success:
            self.console.print(f"[green]✓ Disabled {server_name}[/green]")
        else:
            self.console.print(f"[yellow]Server {server_name} was not enabled[/yellow]")

    def _mcp_status(self) -> None:
        enabled = self.conversation.mcp_manager.get_enabled_servers()
        total_tools = 0

        for server_name in enabled:
            connection = self.conversation.mcp_manager.servers.get(server_name)
            if connection:
                total_tools += len(connection.tools)

        self.console.print("\n[bold]MCP Status:[/bold]\n")
        self.console.print(f"Active servers: {len(enabled)}")
        if enabled:
            for name in enabled:
                connection = self.conversation.mcp_manager.servers.get(name)
                tool_count = len(connection.tools) if connection else 0
                self.console.print(f"  • {name}: {tool_count} tools")
        self.console.print(f"\nTotal MCP tools loaded: {total_tools}")
        self.console.print()

    def _print_welcome(self) -> None:
        self.renderer.render_markdown(
            build_welcome_markdown(self.config.model, self.cwd)
        )

    def _print_goodbye(self) -> None:
        self.console.print("\n[cyan]Goodbye![/cyan]")

    def _print_help(self) -> None:
        self.renderer.render_markdown(build_help_markdown())

    def _print_permissions(self) -> None:
        tools = self.registry.get_all()
        self.console.print(f"\n[bold]Registered Tools ({len(tools)}):[/bold]\n")
        for name in sorted(tools.keys()):
            self.console.print(f"  • {name}")

    def _print_tools(self) -> None:
        tools = self.registry.get_all()
        if not tools:
            self.console.print("[yellow]No tools registered[/yellow]")
            return

        self.console.print("\n[bold]Tool Reference[/bold]\n")
        for name in sorted(tools.keys()):
            tool = tools[name]
            schema = tool.get_schema()
            description = schema.get("description", "(no description)")
            params = schema.get("parameters", {})
            props = params.get("properties", {})
            required = set(params.get("required", []))

            self.console.print(f"[cyan]{name}[/cyan]: {description}")
            if not props:
                self.console.print("  [dim]No parameters[/dim]\n")
                continue

            for prop_name, prop_schema in props.items():
                desc = prop_schema.get("description", "")
                optional = "optional" if prop_name not in required else "required"
                self.console.print(f"  • {prop_name} ({optional}) – {desc}")
            self.console.print("")

    def _print_models(self) -> None:
        selection = self._prompt_model_selection()
        if selection:
            self._apply_model(selection)

    def _prompt_model_selection(self) -> Optional[str]:
        if self._can_use_model_dialog():
            try:
                current = self.client.model
                values = [
                    (name, f"{name} - {desc}") for name, desc in AVAILABLE_MODELS.items()
                ]
                dialog = radiolist_dialog(
                    title="Select GLM Model",
                    text="Use arrow keys and Enter to choose a model.",
                    values=values,
                    default=current if current in AVAILABLE_MODELS else None,
                )
                result = dialog.run()
                if result:
                    return result
            except Exception:
                pass

        self._render_model_list()
        return None

    def _render_model_list(self) -> None:
        models_text = build_models_markdown(AVAILABLE_MODELS.items())
        self.renderer.render_markdown(models_text)

    def _can_use_model_dialog(self) -> bool:
        return bool(
            radiolist_dialog
            and sys.stdin.isatty()
            and sys.stdout.isatty()
        )

    def _apply_model(self, normalized: str) -> None:
        previous = self.client.model
        if normalized == previous:
            self.console.print(f"[yellow]Already using {normalized}[/yellow]")
            return

        self.client.model = normalized
        self.config.model = normalized

        self.console.print(
            f"[green]Switched model to {normalized}[/green] "
            f"(from {previous})"
        )

    def _handle_model_command(self, model_name: str) -> None:
        if not model_name:
            selection = self._prompt_model_selection()
            if selection:
                self._apply_model(selection)
            return

        normalized = model_name.strip()
        if normalized not in AVAILABLE_MODELS:
            self.renderer.render_error(f"Unknown model: {normalized}")
            self.console.print("Use /models to open the model selector.")
            return

        self._apply_model(normalized)

    def _print_tool_output(self, arg: str) -> None:
        history = self.conversation.get_tool_history()
        entries = history.all()
        if not entries:
            self.console.print("[yellow]No tool output available yet[/yellow]")
            return

        index = len(entries) - 1
        if arg:
            try:
                value = int(arg)
            except ValueError:
                self.renderer.render_error("Usage: /toolout [index]")
                return
            if value <= 0:
                self.renderer.render_error("Index must be 1 or greater")
                return
            index = value - 1

        if not (0 <= index < len(entries)):
            self.renderer.render_error(f"No tool output with index {index + 1}")
            return

        entry = entries[index]
        border = "green" if entry.success else "red"
        title = f"Tool Output · {entry.name} (#{index + 1})"
        content = entry.output or "[dim](empty output)[/dim]"
        self.renderer.render_panel(content, title, border_style=border)
        self.console.print(
            f"[dim]Showing tool result {index + 1} of {len(entries)} — use /toolout [index] to view others[/dim]"
        )

    def _is_slash_command(self, user_input: str) -> bool:
        return user_input.startswith("/") and user_input.split(maxsplit=1)[0].lower() in self._command_triggers
