"""Pseudo-terminal smoke test for the CodinGLM CLI."""

from __future__ import annotations

import os
import pty
import re
import select
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_until(fd: int, marker: str, timeout: float = 5.0) -> str:
    """Read from fd until marker is seen or timeout expires."""
    deadline = time.time() + timeout
    chunks: list[bytes] = []

    while time.time() < deadline:
        rlist, _, _ = select.select([fd], [], [], 0.05)
        if not rlist:
            continue

        data = os.read(fd, 4096)
        if not data:
            break

        chunks.append(data)
        joined = b"".join(chunks)
        text = joined.decode(errors="ignore")
        sanitized = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)
        sanitized = re.sub(r"\x1b\].*?\x07", "", sanitized)
        if marker in sanitized:
            return sanitized

    raise AssertionError(f"Timed out waiting for marker: {marker!r}")


def _send_line(fd: int, line: str) -> None:
    os.write(fd, f"{line}\n".encode())


def _read_optional(fd: int, marker: str, timeout: float = 2.0) -> None:
    try:
        _read_until(fd, marker, timeout=timeout)
    except AssertionError:
        pass


def test_cli_end_to_end(tmp_path):
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(PROJECT_ROOT))
    env.setdefault("Z_AI_API_KEY", "test-key")

    master_fd, slave_fd = pty.openpty()

    proc = subprocess.Popen(
        [sys.executable, "-u", str(PROJECT_ROOT / "tests/integration/run_cli.py")],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        env=env,
        cwd=PROJECT_ROOT,
        close_fds=True,
    )

    try:
        _read_until(master_fd, "Type your request")
        _send_line(master_fd, "")

        _send_line(master_fd, "/tools")
        output = _read_until(master_fd, "Bash")
        assert "Tool Reference" in output

        _send_line(master_fd, "integration smoke test")
        tool_output = _read_until(master_fd, "→ Executing: Bash")
        assert "integration smoke" in tool_output

        final_output = _read_until(master_fd, "Tool output captured")
        assert "Tool output captured" in final_output

        _send_line(master_fd, "/exit")
        _read_optional(master_fd, "Goodbye!")
    finally:
        os.close(slave_fd)
        os.close(master_fd)
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
