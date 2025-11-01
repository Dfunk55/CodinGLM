"""CLI entrypoint for CodinGLM."""

from __future__ import annotations

from pathlib import Path

import click

from .cli_app import CodinGLMCLI
from .config import Config


@click.command()
@click.option("--cwd", type=click.Path(exists=True), default=".", help="Working directory")
@click.option("--model", help="Override model from config")
@click.option("--debug/--no-debug", default=True, help="Enable debug mode")
def main(cwd: str, model: str | None, debug: bool) -> None:
    """CodinGLM: Claude Code clone powered by Z.ai."""
    config = Config.load()

    if model:
        config.model = model

    working_dir = Path(cwd).resolve()

    cli = CodinGLMCLI(config=config, cwd=working_dir, debug=debug)
    cli.run()


if __name__ == "__main__":
    main()
