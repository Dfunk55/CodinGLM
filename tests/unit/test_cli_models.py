"""Tests for runtime model switching via CLI commands."""

from pathlib import Path

import pytest

from codinglm.cli_app import CodinGLMCLI
from codinglm.config import Config


@pytest.fixture
def cli(monkeypatch) -> CodinGLMCLI:
    """Create a CLI instance with a stubbed prompt session."""

    class DummySession:
        def __init__(self, *args, **kwargs):
            pass

        def prompt(self, *args, **kwargs):
            raise RuntimeError("prompt should not be used in tests")

    monkeypatch.setattr(
        "codinglm.ui.prompt.PromptSessionFactory.build",
        lambda self: DummySession(),
    )

    config = Config(apiKey="test-key", model="glm-4.6")
    return CodinGLMCLI(config=config, cwd=Path.cwd(), debug=False)


def test_model_command_switches_model(cli: CodinGLMCLI) -> None:
    cli._handle_model_command("glm-4.5-air")
    assert cli.client.model == "glm-4.5-air"
    assert cli.config.model == "glm-4.5-air"


def test_model_command_unknown_model(cli: CodinGLMCLI) -> None:
    cli._handle_model_command("unknown-model")
    # Should remain unchanged
    assert cli.client.model == "glm-4.6"
    assert cli.config.model == "glm-4.6"


def test_model_command_without_argument_lists_options(cli: CodinGLMCLI) -> None:
    cli._handle_model_command("")
    # No state change expected
    assert cli.client.model == "glm-4.6"


def test_models_command_interactive_selection(monkeypatch, cli: CodinGLMCLI) -> None:
    monkeypatch.setattr(cli, "_can_use_model_dialog", lambda: True)

    class DummyDialog:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            return "glm-4.5-air"

    monkeypatch.setattr(
        "codinglm.cli_app.radiolist_dialog",
        lambda **kwargs: DummyDialog(**kwargs),
    )

    cli._print_models()
    assert cli.client.model == "glm-4.5-air"
    assert cli.config.model == "glm-4.5-air"
