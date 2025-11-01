"""Tests for tool system."""

from pathlib import Path
import tempfile
import time

import pytest

from codinglm.tools.file_ops import Read, Write, Edit, Glob
from codinglm.tools.base import ToolRegistry
from codinglm.tools.bash import Bash, BashOutput, KillShell


def test_read_tool():
    """Test Read tool."""
    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("line 1\nline 2\nline 3")
        temp_path = f.name

    try:
        tool = Read()
        result = tool.execute(path=temp_path)
        assert result.success
        assert "line 1" in result.output
    finally:
        Path(temp_path).unlink()


def test_write_tool():
    """Test Write tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.txt"
        tool = Write()
        result = tool.execute(path=str(file_path), content="Hello, world!")

        assert result.success
        assert file_path.exists()
        assert file_path.read_text() == "Hello, world!"


def test_edit_tool():
    """Test Edit tool."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Hello, world!")
        temp_path = f.name

    try:
        tool = Edit()
        result = tool.execute(
            path=temp_path,
            old_string="world",
            new_string="CodinGLM",
        )

        assert result.success
        assert Path(temp_path).read_text() == "Hello, CodinGLM!"
    finally:
        Path(temp_path).unlink()


def test_tool_registry():
    """Test ToolRegistry."""
    registry = ToolRegistry()
    read_tool = Read()
    registry.register(read_tool)

    assert registry.get("Read") == read_tool
    assert len(registry.get_all()) == 1
    assert len(registry.get_function_definitions()) == 1


def test_write_tool_aliases():
    """Write tool should accept legacy parameter names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "alias.txt"
        tool = Write()
        result = tool.execute(file_path=str(file_path), contents="Alias content")

        assert result.success
        assert file_path.read_text() == "Alias content"


def test_tool_registry_executes_with_path_json():
    """ToolRegistry should execute using JSON arguments with modern keys."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("alpha\nbeta\ngamma")
        temp_path = f.name

    try:
        registry = ToolRegistry()
        registry.register(Read())

        result = registry.execute(
            "Read",
            '{"path": "%s", "offset": 2, "limit": 1}' % temp_path.replace("\\", "\\\\"),
        )

        assert result.success
        assert "beta" in result.output
    finally:
        Path(temp_path).unlink()


def test_bash_tool_accepts_aliases():
    """Bash tool should accept alias parameters."""
    bash = Bash()
    result = bash.execute(commands=["echo hello", "echo world"])
    assert result.success
    assert "hello" in result.output
    assert "world" in result.output


def test_bash_tool_missing_command_error():
    """Bash tool should return friendly error when command is missing."""
    bash = Bash()
    result = bash.execute()
    assert not result.success
    assert "Missing required parameter" in (result.error or "")


def test_bash_output_and_kill_aliases():
    """BashOutput and KillShell should accept alias identifiers."""
    bash = Bash()
    start = bash.execute(command="sleep 0.1", run_in_background=True)
    assert start.success
    job_id_line = start.output.splitlines()[0]
    job_id = job_id_line.split(":")[1].strip()

    # Give the background job a moment to finish
    time.sleep(0.2)

    output_tool = BashOutput(bash)
    output_result = output_tool.execute(job_id=job_id)
    assert output_result.success

    kill_tool = KillShell(bash)
    kill_result = kill_tool.execute(id=job_id)
    assert kill_result.success
