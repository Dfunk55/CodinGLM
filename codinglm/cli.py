"""Main CLI for CodinGLM."""

import click
import os
import select
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

try:
    from prompt_toolkit.shortcuts import radiolist_dialog
except Exception:  # pragma: no cover - dialog optional at runtime
    radiolist_dialog = None  # type: ignore

from .config import Config
from .api.client import GLMClient
from .logging import DebugEventLogger, TranscriptConsole
from .conversation.manager import ConversationManager
from .tools.registry import get_default_registry
from .ui.renderer import MarkdownRenderer

try:
    import termios
    import tty
except ImportError:  # pragma: no cover - non-POSIX platforms
    termios = None  # type: ignore
    tty = None  # type: ignore


class StreamInterruptWatcher:
    """Monitor stdin for ESC key to interrupt streaming output."""

    def __init__(self):
        self._fd: Optional[int] = None
        self._original_attrs: Optional[Sequence[int]] = None  # type: ignore[type-arg]
        self._listener: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._interrupted = threading.Event()

        if sys.stdin.isatty() and termios and tty:
            try:
                self._fd = sys.stdin.fileno()
                self._original_attrs = termios.tcgetattr(self._fd)  # type: ignore[arg-type]
            except Exception:
                self._fd = None
                self._original_attrs = None

    def start(self) -> None:
        """Begin listening for ESC keypress."""
        if self._fd is None or not termios or not tty:
            return

        try:
            tty.setcbreak(self._fd)  # type: ignore[arg-type]
        except Exception:
            self._fd = None
            return

        self._listener = threading.Thread(target=self._listen, daemon=True)
        self._listener.start()

    def _listen(self) -> None:
        """Listen loop for ESC key."""
        if self._fd is None:
            return

        while not self._stop_event.is_set():
            try:
                ready, _, _ = select.select([self._fd], [], [], 0.05)
            except Exception:
                break

            if ready:
                try:
                    data = os.read(self._fd, 1)
                except Exception:
                    break

                if data == b"\x1b":  # ESC
                    self._interrupted.set()
                    self._stop_event.set()
                    break

        self._stop_event.set()

    def should_stop(self) -> bool:
        """Return True if streaming should be interrupted."""
        return self._interrupted.is_set()

    def stop(self) -> bool:
        """Stop listening and restore terminal state.

        Returns:
            True if an interrupt was triggered.
        """
        if self._fd is None:
            return self._interrupted.is_set()

        self._stop_event.set()
        if self._listener:
            self._listener.join(timeout=0.1)

        if self._original_attrs is not None and termios:
            try:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._original_attrs)  # type: ignore[arg-type]
            except Exception:
                pass

        return self._interrupted.is_set()


AVAILABLE_MODELS: Dict[str, str] = {
    "glm-4.6": "Flagship GLM Coding Plan model (recommended)",
    "glm-4.5-air": "Fast, cost-effective coding model",
    "glm-4-flash": "Ultra-fast responses for quick tasks",
}


class CodinGLMCLI:
    """Main CLI application."""

    def __init__(
        self,
        config: Config,
        cwd: Path,
        debug: bool = True,
    ):
        """Initialize CLI.

        Args:
            config: Configuration
            cwd: Working directory
            debug: Enable debug mode (defaults to True for full transcripts)
        """
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

        # Initialize console + debug logging artifacts
        self.console = TranscriptConsole(
            transcript_path=transcript_path,
            soft_wrap=True,
        )
        self.renderer = MarkdownRenderer(self.console)
        self.debug_log_path = transcript_path
        self.debug_logger = DebugEventLogger(debug_events_path) if debug_events_path else None

        if self.debug and transcript_path:
            self.console.print(
                f"[dim]Debug transcript active → {transcript_path}[/dim]"
            )
        if self.debug_logger:
            self.console.print(
                f"[dim]Structured debug events → {self.debug_logger.path}[/dim]"
            )
            self._emit_debug_event(
                "session_start",
                "CodinGLM session started",
                {"session_id": self.session_id, "cwd": str(self.cwd)},
            )

        # Initialize API client
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
        except ValueError as e:
            self.console.print(f"[red]Configuration error: {e}[/red]")
            sys.exit(1)

        # Initialize tools and conversation
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

        # Prompt session with history
        history_file = Path.home() / ".codinglm-history"
        self.session = PromptSession(history=FileHistory(str(history_file)))
        self._shutdown_done = False

    def _emit_debug_event(
        self,
        event: str,
        message: str,
        extra: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Helper to record structured debug events."""
        if not self.debug_logger:
            return

        payload: Dict[str, Any] = {"session_id": self.session_id}
        if extra:
            payload.update(extra)
        self.debug_logger.emit(event, message, payload)

    def _shutdown(self) -> None:
        """Close logging resources exactly once."""
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
        """Run the interactive REPL."""
        self._print_welcome()

        try:
            while True:
                try:
                    # Get user input
                    user_input = self.session.prompt("\n> ")

                    if not user_input.strip():
                        continue

                    self._emit_debug_event(
                        "user_input",
                        "User submitted input",
                        {"content": user_input},
                    )

                    # Handle commands
                    if user_input.startswith("/"):
                        self._handle_command(user_input)
                        continue

                    # Add user message
                    self.conversation.add_user_message(user_input)
                    self._emit_debug_event(
                        "conversation_turn",
                        "Conversation turn started",
                        {"message_count": len(self.conversation.messages)},
                    )

                    # Run conversation turn
                    self.console.print("\n[bold]Assistant:[/bold]\n")
                    interrupt = StreamInterruptWatcher()
                    interrupt.start()
                    try:
                        self.conversation.run_turn(
                            stream=True,
                            should_stop=interrupt.should_stop,
                        )
                    finally:
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
                except Exception as e:
                    self._emit_debug_event(
                        "cli_error",
                        "CLI raised exception",
                        {"exception": repr(e)},
                    )
                    if self.debug:
                        raise
                    self.renderer.render_error(str(e))
        finally:
            self._shutdown()

        self._print_goodbye()

    def _handle_command(self, command: str) -> None:
        """Handle slash commands.

        Args:
            command: Command string
        """
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        self._emit_debug_event(
            "slash_command",
            "Slash command invoked",
            {"command": cmd, "args": args},
        )

        if cmd == "/exit" or cmd == "/quit":
            self._print_goodbye()
            self._shutdown()
            sys.exit(0)

        elif cmd == "/clear":
            self.conversation.clear_history()

        elif cmd == "/compact":
            self._handle_compact_command()

        elif cmd == "/metrics":
            self._handle_metrics_command()

        elif cmd == "/help":
            self._print_help()

        elif cmd == "/permissions":
            self._print_permissions()

        elif cmd == "/models":
            self._print_models()

        elif cmd == "/model":
            self._handle_model_command(args.strip())

        elif cmd == "/tools":
            self._print_tools()

        elif cmd == "/mcp":
            self._handle_mcp_command(args.strip())

        else:
            self.renderer.render_error(f"Unknown command: {command}")
            self.console.print("Type /help for available commands")

    def _handle_compact_command(self) -> None:
        """Manually trigger context compression."""
        from .utils.token_counter import estimate_messages_tokens

        # Get current token count
        tokens_before = estimate_messages_tokens(self.conversation.messages)
        messages_before = len(self.conversation.messages)

        # Trigger compression
        self.conversation.compressor.maybe_compress(
            self.conversation.messages,
            trigger="manual"
        )

        # Get metrics after compression
        tokens_after = estimate_messages_tokens(self.conversation.messages)
        messages_after = len(self.conversation.messages)

        # Show results
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
                f"[green]✓ Context compressed[/green]\n"
                f"Removed: {messages_removed} messages\n"
                f"Tokens: {tokens_before:,} → {tokens_after:,} (saved {tokens_saved:,}, {reduction_pct:.1f}%)"
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
        """Display compression metrics collected so far."""
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
        """Handle MCP server management commands.

        Args:
            args: Command arguments
        """
        import asyncio

        parts = args.split(maxsplit=1)
        if not parts:
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
        """List available MCP servers."""
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
        """Enable an MCP server."""
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
        """Disable an MCP server."""
        self.console.print(f"[cyan]Disabling MCP server: {server_name}[/cyan]")
        success = await self.conversation.mcp_manager.disable_server(server_name)

        if success:
            self.console.print(f"[green]✓ Disabled {server_name}[/green]")
        else:
            self.console.print(f"[yellow]Server {server_name} was not enabled[/yellow]")

    def _mcp_status(self) -> None:
        """Show MCP server status."""
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
        """Print welcome message."""
        welcome = f"""# CodinGLM

Powered by Z.ai's {self.config.model}

Working directory: {self.cwd}

Type your request or use commands:
- /help - Show help
- /clear - Clear history
- /compact - Compress context
- /exit - Exit

"""
        self.renderer.render_markdown(welcome)

    def _print_goodbye(self) -> None:
        """Print goodbye message."""
        self.console.print("\n[cyan]Goodbye![/cyan]")

    def _print_help(self) -> None:
        """Print help message."""
        help_text = """# Available Commands

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
        self.renderer.render_markdown(help_text)

    def _print_permissions(self) -> None:
        """Print tool permissions."""
        tools = self.registry.get_all()
        self.console.print(f"\n[bold]Registered Tools ({len(tools)}):[/bold]\n")
        for name in sorted(tools.keys()):
            self.console.print(f"  • {name}")

    def _print_tools(self) -> None:
        """Display detailed tool schemas for reference."""
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
        """Open interactive model selector or fall back to text list."""
        selection = self._prompt_model_selection()
        if selection:
            self._apply_model(selection)

    def _prompt_model_selection(self) -> Optional[str]:
        """Prompt the user to choose a model, returning the selection if any."""
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
        """Render model list in plain text."""
        models_text = """# Available Models

- `glm-4.6` - Flagship GLM Coding Plan model (recommended)
- `glm-4.5-air` - Fast, cost-effective coding model
- `glm-4-flash` - Ultra-fast responses for quick tasks

Use `/model <name>` or `/models` to switch models.
"""
        self.renderer.render_markdown(models_text)

    def _can_use_model_dialog(self) -> bool:
        """Check whether we can show an interactive dialog."""
        return bool(
            radiolist_dialog
            and sys.stdin.isatty()
            and sys.stdout.isatty()
        )

    def _apply_model(self, normalized: str) -> None:
        """Apply the selected model and report the change."""
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
        """Switch the active model at runtime."""
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


@click.command()
@click.option("--cwd", type=click.Path(exists=True), default=".", help="Working directory")
@click.option("--model", help="Override model from config")
@click.option("--debug/--no-debug", default=True, help="Enable debug mode")
def main(cwd: str, model: str | None, debug: bool) -> None:
    """CodinGLM: Claude Code clone powered by Z.ai."""
    # Load configuration
    config = Config.load()

    # Override model if specified
    if model:
        config.model = model

    # Convert cwd to Path
    working_dir = Path(cwd).resolve()

    # Create and run CLI
    cli = CodinGLMCLI(config=config, cwd=working_dir, debug=debug)
    cli.run()


if __name__ == "__main__":
    main()
