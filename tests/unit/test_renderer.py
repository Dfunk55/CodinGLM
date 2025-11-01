"""Tests for the MarkdownRenderer utilities."""

from __future__ import annotations

from rich.console import Console

from codinglm.ui.renderer import MarkdownRenderer


def _build_renderer(width: int = 60) -> tuple[MarkdownRenderer, Console]:
    console = Console(width=width, record=True, soft_wrap=True, color_system=None)
    return MarkdownRenderer(console), console


def test_assistant_markdown_wraps_long_paragraph():
    """Assistant panels should wrap long paragraphs instead of truncating them."""
    renderer, console = _build_renderer()
    renderer.render_assistant_markdown(" ".join(["word"] * 40))
    output_lines = console.export_text().splitlines()
    content_lines = [line for line in output_lines if line.startswith("│")]

    assert len(content_lines) > 1
    # Ensure we didn't lose the final word during wrapping.
    assert "word" in content_lines[-1]


def test_wrap_markdown_preserves_code_blocks():
    """Code fence content should remain untouched by the wrapping helper."""
    renderer, _ = _build_renderer()
    text = "```python\nprint('hello world')\n```"
    wrapped = renderer.wrap_markdown_text(text)
    lines = wrapped.splitlines()

    assert lines[0] == "```python"
    assert lines[1] == "print('hello world')"
    assert lines[2] == "```"


def test_wrap_markdown_indents_list_items():
    """List items should maintain indentation when wrapped."""
    renderer, _ = _build_renderer()
    wrapped = renderer.wrap_markdown_text("- " + " ".join(["item"] * 12))
    lines = wrapped.splitlines()

    assert lines[0].startswith("- ")
    assert all(line.startswith("  ") for line in lines[1:])
