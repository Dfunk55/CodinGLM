"""Tests for prompt session key bindings."""

from __future__ import annotations

from prompt_toolkit.keys import Keys

from codinglm.ui.prompt import PromptSessionFactory


def test_prompt_enter_submits_by_default() -> None:
    """Ensure Enter remains unbound so the buffer submits by default."""
    key_bindings = PromptSessionFactory._build_key_bindings()
    # Newline shortcut should still be available via Ctrl+J.
    assert any(Keys.ControlJ in binding.keys for binding in key_bindings.bindings)
    # Enter (Ctrl+M) must not be rebound to avoid intercepting submissions.
    assert all(Keys.ControlM not in binding.keys for binding in key_bindings.bindings)
