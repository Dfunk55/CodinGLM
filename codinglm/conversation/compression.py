"""Automatic conversation context compression."""

from __future__ import annotations

import logging
import textwrap
import uuid
from typing import Callable, List, Optional, Sequence, Tuple

import httpx
from rich.console import Console

from ..api.client import GLMClient
from ..api.models import Message
from ..config import ContextCompressionConfig
from ..utils.token_counter import estimate_messages_tokens

# Identifier used to tag synthetic summary messages.
SUMMARY_NAME = "context_summary"

# Configuration constants for compression behavior
MIN_SUMMARY_CHARS = 200  # Minimum characters in a summary
CHARS_PER_TOKEN_ESTIMATE = 4  # Rough character-to-token ratio
FALLBACK_MAX_SNIPPETS = 10  # Max snippets in fallback summary
FALLBACK_SNIPPET_LENGTH = 160  # Max length per snippet in fallback
DISPLAY_TRUNCATE_LENGTH = 500  # Truncate tool output display to this length
MIN_COMPRESSION_REDUCTION_RATIO = 0.10  # Minimum 10% token reduction per pass


class CompressionMetrics:
    """Track compression effectiveness metrics."""

    def __init__(self):
        self.total_compressions = 0
        self.total_tokens_before = 0
        self.total_tokens_after = 0
        self.total_messages_compressed = 0
        self.api_calls_successful = 0
        self.fallback_summaries_used = 0

    def record_compression(
        self,
        tokens_before: int,
        tokens_after: int,
        messages_count: int,
        used_api: bool,
    ) -> None:
        """Record a compression event."""
        self.total_compressions += 1
        self.total_tokens_before += tokens_before
        self.total_tokens_after += tokens_after
        self.total_messages_compressed += messages_count
        if used_api:
            self.api_calls_successful += 1
        else:
            self.fallback_summaries_used += 1

    def get_compression_ratio(self) -> float:
        """Calculate average compression ratio (tokens saved / tokens before)."""
        if self.total_tokens_before == 0:
            return 0.0
        return 1.0 - (self.total_tokens_after / self.total_tokens_before)

    def get_tokens_saved(self) -> int:
        """Get total tokens saved by compression."""
        return self.total_tokens_before - self.total_tokens_after

    def __str__(self) -> str:
        """Return human-readable metrics summary."""
        if self.total_compressions == 0:
            return "No compressions performed yet."

        ratio = self.get_compression_ratio()
        saved = self.get_tokens_saved()
        return (
            f"Compressions: {self.total_compressions} | "
            f"Messages compressed: {self.total_messages_compressed} | "
            f"Tokens saved: {saved} ({ratio:.1%}) | "
            f"API: {self.api_calls_successful} | Fallback: {self.fallback_summaries_used}"
        )


class ContextCompressor:
    """Maintains conversation history within token limits via summarisation."""

    def __init__(
        self,
        client: Optional[GLMClient],
        console: Console,
        config: Optional[ContextCompressionConfig] = None,
        summarize_override: Optional[Callable[[Sequence[Message]], str]] = None,
    ):
        self.client = client
        self.console = console
        self.config = config or ContextCompressionConfig()
        self._summarize_override = summarize_override
        self._compression_count = 0
        self.metrics = CompressionMetrics()
        self._summary_marker = f"{SUMMARY_NAME}:{uuid.uuid4().hex[:8]}"

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def reset(self) -> None:
        """Reset internal counters (useful after clearing history)."""
        self._compression_count = 0

    def reset_metrics(self) -> None:
        """Reset compression metrics."""
        self.metrics = CompressionMetrics()

    def get_metrics(self) -> CompressionMetrics:
        """Get current compression metrics.

        Returns:
            CompressionMetrics object with statistics
        """
        return self.metrics

    def maybe_compress(self, messages: List[Message], trigger: str = "") -> None:
        """Compress conversation history when it exceeds configured limits."""
        if not self.config.enabled:
            return

        for pass_index in range(max(1, self.config.maxCompressionPasses)):
            tokens_before = estimate_messages_tokens(messages)
            if tokens_before <= self.config.maxContextTokens:
                return

            compressed = self._compress_once(messages, tokens_before, trigger, pass_index)
            if not compressed:
                return

            tokens_after = estimate_messages_tokens(messages)

            # Check convergence: if we didn't save enough tokens, stop iterating
            if tokens_before > 0:
                reduction_ratio = (tokens_before - tokens_after) / tokens_before
                if reduction_ratio < MIN_COMPRESSION_REDUCTION_RATIO:
                    if self.config.verbose:
                        self.console.print(
                            f"[dim]Compression stopped: insufficient reduction "
                            f"({reduction_ratio:.1%} < {MIN_COMPRESSION_REDUCTION_RATIO:.0%})[/dim]"
                        )
                    return

            if tokens_after <= self.config.targetContextTokens:
                return

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _compress_once(
        self,
        messages: List[Message],
        total_tokens: int,
        trigger: str,
        pass_index: int,
    ) -> bool:
        """Perform a single compression pass."""
        span = self._select_span(messages)
        if span is None:
            if self.config.verbose:
                non_system_count = sum(1 for m in messages if m.role != "system")
                # Determine the actual reason for skipping
                if non_system_count == 0:
                    reason = "no non-system messages"
                elif non_system_count <= self.config.preserveRecentMessages:
                    reason = f"only {non_system_count} messages (≤ preserveRecentMessages={self.config.preserveRecentMessages})"
                else:
                    reason = "all messages already compressed"
                self.console.print(
                    f"[dim]Context compression skipped: {reason}. "
                    f"Consider increasing maxContextTokens or decreasing preserveRecentMessages.[/dim]"
                )
            return False

        start, end = span
        window = messages[start:end]
        if not window:
            return False

        estimated_window_tokens = estimate_messages_tokens(window)
        summary_text, used_api = self._summarize(window)
        summary_text = self._truncate_summary(summary_text)

        summary_content = self._format_summary(
            summary_text=summary_text,
            window=window,
            window_tokens=estimated_window_tokens,
            total_tokens=total_tokens,
            trigger=trigger,
            pass_index=pass_index,
        )

        summary_message = Message(
            role="assistant",
            name=self._summary_marker,
            content=summary_content,
        )

        # Calculate tokens after compression (estimate with just summary message)
        estimated_summary_tokens = estimate_messages_tokens([summary_message])

        messages[start:end] = [summary_message]
        self._compression_count += 1

        # Record metrics with actual API usage (determined during summarization)
        self.metrics.record_compression(
            tokens_before=estimated_window_tokens,
            tokens_after=estimated_summary_tokens,
            messages_count=len(window),
            used_api=used_api,
        )

        self._log_compression(len(window), estimated_window_tokens, trigger or "automatic")
        return True

    def _select_span(self, messages: List[Message]) -> Optional[Tuple[int, int]]:
        """Select a contiguous span of messages to summarise."""
        non_system_indices = [idx for idx, message in enumerate(messages) if message.role != "system"]
        if not non_system_indices:
            return None

        # Note: preserve is always >= 1 due to config validation, so the preserve == 0 case is unreachable
        preserve = self.config.preserveRecentMessages
        if len(non_system_indices) <= preserve:
            return None

        tail_start = non_system_indices[-preserve]

        start_index = non_system_indices[0]
        if tail_start <= start_index:
            return None

        span = messages[start_index:tail_start]
        if not span:
            return None

        # Check if all messages in span are already summaries (prevents infinite loops)
        if all(
            message.name and message.name.startswith(f"{SUMMARY_NAME}:")
            for message in span
        ):
            return None

        return start_index, tail_start

    def _summarize(self, window: Sequence[Message]) -> Tuple[str, bool]:
        """Generate a summary for the provided window.

        Returns:
            Tuple of (summary_text, used_api) where used_api indicates if the API was successfully used
        """
        if self._summarize_override:
            return self._summarize_override(window), False

        if not self.client:
            return self._fallback_summary(window), False

        prompt_messages = self._build_summariser_prompt(window)

        original_model: Optional[str] = None
        if self.config.summaryModel:
            original_model = self.client.model
            self.client.model = self.config.summaryModel

        try:
            response = self.client.chat(messages=list(prompt_messages), tools=None, stream=False)
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            # Network or timeout errors - use fallback
            if self.config.verbose:
                self.console.print(
                    f"[yellow]Compression summary failed (network): {exc.__class__.__name__}[/yellow]"
                )
            logging.debug(f"Network error during compression summary: {exc}")
            return self._fallback_summary(window), False
        except (KeyError, ValueError, TypeError) as exc:
            # API response parsing errors - use fallback
            if self.config.verbose:
                self.console.print(
                    f"[yellow]Compression summary failed (parsing): {exc.__class__.__name__}[/yellow]"
                )
            logging.debug(f"Parsing error during compression summary: {exc}")
            return self._fallback_summary(window), False
        except Exception as exc:  # pragma: no cover - unexpected errors
            # Catch-all for unexpected errors
            if self.config.verbose:
                self.console.print(f"[yellow]Compression summary failed (unexpected): {exc}[/yellow]")
            logging.exception("Unexpected error during compression summary")
            return self._fallback_summary(window), False
        finally:
            if original_model is not None:
                self.client.model = original_model

        if isinstance(response, list):
            return self._fallback_summary(window), False

        summary = (response or "").strip()
        if not summary:
            return self._fallback_summary(window), False
        return summary, True

    def _build_summariser_prompt(self, window: Sequence[Message]) -> Sequence[Message]:
        """Construct messages instructing the model to summarise."""
        transcript = self._render_transcript(window)
        max_chars = max(MIN_SUMMARY_CHARS, self.config.summaryMaxTokens * CHARS_PER_TOKEN_ESTIMATE)

        instructions = textwrap.dedent(
            f"""
            Summarise the coding session conversation below.
            Focus on:
            - Key objectives, decisions, and conclusions.
            - File paths, commands, and code changes mentioned.
            - Outstanding tasks, questions, or follow-ups.

            Output <= {max_chars} characters. Use concise bullet points when possible.
            """
        ).strip()

        return [
            Message(
                role="system",
                content="You condense developer conversations into durable context summaries.",
            ),
            Message(
                role="user",
                content=f"{instructions}\n\n<conversation>\n{transcript}\n</conversation>",
            ),
        ]

    def _fallback_summary(self, window: Sequence[Message]) -> str:
        """Fallback summary if the model cannot be contacted."""
        snippets: List[str] = []
        for message in window:
            content = (message.content or "").strip()
            if not content:
                continue
            head = content.splitlines()[0][:FALLBACK_SNIPPET_LENGTH]
            label = message.name or message.role
            snippets.append(f"- {label}: {head}")
            if len(snippets) >= FALLBACK_MAX_SNIPPETS:
                break

        if not snippets:
            return "Earlier conversation compressed. No textual content captured."

        return "Key points kept due to local fallback:\n" + "\n".join(snippets)

    def _truncate_summary(self, summary_text: str) -> str:
        """Ensure the summary respects the configured character budget."""
        max_chars = max(MIN_SUMMARY_CHARS, self.config.summaryMaxTokens * CHARS_PER_TOKEN_ESTIMATE)
        summary = summary_text.strip()
        if len(summary) <= max_chars:
            return summary
        return summary[:max_chars].rsplit("\n", 1)[0].rstrip()

    def _format_summary(
        self,
        summary_text: str,
        window: Sequence[Message],
        window_tokens: int,
        total_tokens: int,
        trigger: str,
        pass_index: int,
    ) -> str:
        """Embed metadata so the assistant treats the summary correctly."""
        turn_count = len(window)
        covered_roles = f"{window[0].role}→{window[-1].role}"
        metadata = (
            f"[context compression #{self._compression_count + 1} | "
            f"span: {turn_count} messages ({covered_roles}); "
            f"was ≈{window_tokens} tokens of ≈{total_tokens}]"
        )

        guidance = (
            "Use this summary instead of asking the user to repeat earlier details. "
            "Assume the compressed messages already occurred."
        )

        trigger_note = f"Triggered by: {trigger or 'automatic'} (pass {pass_index + 1})."

        parts = [
            metadata,
            trigger_note,
            "",
            summary_text,
            "",
            guidance,
        ]
        return "\n".join(parts).strip()

    def _render_transcript(self, window: Sequence[Message]) -> str:
        """Render a human-readable transcript for the summariser."""
        lines: List[str] = []
        for message in window:
            label = (message.name or message.role).upper()
            content = (message.content or "").strip()
            if content:
                lines.append(f"{label}: {content}")
            else:
                lines.append(f"{label}: (no textual content)")
        return "\n".join(lines)

    def _log_compression(self, message_count: int, tokens: int, trigger: str) -> None:
        """Log that compression occurred."""
        notice = (
            f"[dim]Context compressed (removed {message_count} messages ≈{tokens} tokens; "
            f"trigger: {trigger}).[/dim]"
        )
        self.console.print(notice)


__all__ = [
    "ContextCompressor",
    "CompressionMetrics",
    "SUMMARY_NAME",
    "DISPLAY_TRUNCATE_LENGTH",
    "MIN_SUMMARY_CHARS",
    "CHARS_PER_TOKEN_ESTIMATE",
    "FALLBACK_MAX_SNIPPETS",
    "FALLBACK_SNIPPET_LENGTH",
    "MIN_COMPRESSION_REDUCTION_RATIO",
]
