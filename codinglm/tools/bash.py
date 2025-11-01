"""Bash execution tool with background job support."""

import subprocess
import threading
import uuid
from typing import Any, Dict, Optional, Sequence, Union
from .base import Tool, ToolResult


class BackgroundJob:
    """A background bash job."""

    def __init__(self, job_id: str, command: str, timeout: int):
        """Initialize background job.

        Args:
            job_id: Unique job ID
            command: Command to execute
            timeout: Timeout in milliseconds
        """
        self.job_id = job_id
        self.command = command
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.stdout: str = ""
        self.stderr: str = ""
        self.returncode: Optional[int] = None
        self.running = False
        self.error: Optional[str] = None

    def start(self) -> None:
        """Start the background job."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        """Run the command in background."""
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            timeout_seconds = self.timeout / 1000 if self.timeout else None
            stdout, stderr = self.process.communicate(timeout=timeout_seconds)

            self.stdout = stdout
            self.stderr = stderr
            self.returncode = self.process.returncode

        except subprocess.TimeoutExpired:
            if self.process:
                self.process.kill()
                self.error = f"Command timed out after {self.timeout}ms"
        except Exception as e:
            self.error = str(e)
        finally:
            self.running = False

    def get_output(self, filter_regex: Optional[str] = None) -> str:
        """Get current output.

        Args:
            filter_regex: Optional regex to filter output lines

        Returns:
            Combined stdout and stderr
        """
        output = self.stdout + self.stderr
        if filter_regex:
            import re

            lines = output.split("\n")
            filtered = [line for line in lines if re.search(filter_regex, line)]
            return "\n".join(filtered)
        return output


class Bash(Tool):
    """Execute bash commands."""

    def __init__(self):
        """Initialize Bash tool."""
        super().__init__()
        self._jobs: Dict[str, BackgroundJob] = {}

    def execute(
        self,
        command: Optional[str] = None,
        commands: Optional[Union[str, Sequence[str]]] = None,
        cmd: Optional[str] = None,
        script: Optional[str] = None,
        shell_command: Optional[str] = None,
        description: Optional[str] = None,
        timeout: int = 120000,  # 2 minutes default
        run_in_background: bool = False,
    ) -> ToolResult:
        """Execute a bash command.

        Args:
            command: The command to execute
            description: Description of what the command does
            timeout: Timeout in milliseconds (max 600000 / 10 min)
            run_in_background: Run command in background

        Returns:
            ToolResult with command output
        """
        try:
            resolved_command = self._resolve_command(
                command=command,
                commands=commands,
                cmd=cmd,
                script=script,
                shell_command=shell_command,
            )

            if not resolved_command:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'command'",
                )

            # Validate timeout
            if timeout > 600000:
                timeout = 600000

            if run_in_background:
                # Start background job
                job_id = str(uuid.uuid4())[:8]
                job = BackgroundJob(job_id, resolved_command, timeout)
                self._jobs[job_id] = job
                job.start()

                return ToolResult(
                    success=True,
                    output=f"Background job started: {job_id}\nCommand: {resolved_command}",
                )

            else:
                # Run synchronously
                result = subprocess.run(
                    resolved_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout / 1000,
                )

                output = result.stdout
                if result.stderr:
                    output += "\n" + result.stderr

                # Truncate if too long
                if len(output) > 30000:
                    output = output[:30000] + "\n... [output truncated]"

                return ToolResult(
                    success=result.returncode == 0,
                    output=output.strip() if output else "Tool ran without output or errors",
                    error=None if result.returncode == 0 else f"Exit code: {result.returncode}",
                )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout}ms",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_job_output(self, job_id: str, filter_regex: Optional[str] = None) -> ToolResult:
        """Get output from a background job.

        Args:
            job_id: Job ID
            filter_regex: Optional regex to filter lines

        Returns:
            ToolResult with job output
        """
        job = self._jobs.get(job_id)
        if not job:
            return ToolResult(
                success=False,
                output="",
                error=f"Job not found: {job_id}",
            )

        output = job.get_output(filter_regex)
        status = "running" if job.running else "completed"

        if job.error:
            return ToolResult(
                success=False,
                output=output,
                error=f"Job {status}: {job.error}",
            )

        return ToolResult(
            success=True,
            output=f"Job {status}\n{output}" if output else f"Job {status} (no output yet)",
        )

    def kill_job(self, job_id: str) -> ToolResult:
        """Kill a background job.

        Args:
            job_id: Job ID to kill

        Returns:
            ToolResult
        """
        job = self._jobs.get(job_id)
        if not job:
            return ToolResult(
                success=False,
                output="",
                error=f"Job not found: {job_id}",
            )

        if job.process and job.running:
            job.process.kill()
            return ToolResult(
                success=True,
                output=f"Job {job_id} killed",
            )

        return ToolResult(
            success=True,
            output=f"Job {job_id} already completed",
        )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Bash tool."""
        return {
            "name": "Bash",
            "description": "Executes bash commands with optional timeout and background execution",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute",
                    },
                    "commands": {
                        "type": ["string", "array"],
                        "description": "Optional alias: string or array of commands joined with newlines",
                    },
                    "cmd": {
                        "type": "string",
                        "description": "Optional alias for command",
                    },
                    "script": {
                        "type": "string",
                        "description": "Optional alias for command",
                    },
                    "shell_command": {
                        "type": "string",
                        "description": "Optional alias for command",
                    },
                    "description": {
                        "type": "string",
                        "description": "Clear description of what this command does (5-10 words)",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Optional timeout in milliseconds (max 600000, default 120000)",
                    },
                    "run_in_background": {
                        "type": "boolean",
                        "description": "Set to true to run command in background",
                    },
                },
                "required": ["command"],
            },
        }

    @staticmethod
    def _resolve_command(
        *,
        command: Optional[str],
        commands: Optional[Union[str, Sequence[str]]],
        cmd: Optional[str],
        script: Optional[str],
        shell_command: Optional[str],
    ) -> Optional[str]:
        """Resolve command from various alias parameters."""
        if command:
            return command
        if cmd:
            return cmd
        if shell_command:
            return shell_command
        if script:
            return script
        if commands:
            if isinstance(commands, str):
                return commands
            if isinstance(commands, Sequence):
                return "\n".join(str(item) for item in commands)
        return None


class BashOutput(Tool):
    """Get output from a background bash job."""

    def __init__(self, bash_tool: Bash):
        """Initialize BashOutput tool.

        Args:
            bash_tool: Reference to Bash tool for accessing jobs
        """
        super().__init__()
        self.bash_tool = bash_tool

    def execute(
        self,
        bash_id: Optional[str] = None,
        job_id: Optional[str] = None,
        id: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> ToolResult:
        """Get output from background job.

        Args:
            bash_id: Job ID
            filter: Optional regex to filter output lines

        Returns:
            ToolResult with job output
        """
        target_id = bash_id or job_id or id
        if not target_id:
            return ToolResult(
                success=False,
                output="",
                error="Missing required parameter 'bash_id'",
            )
        return self.bash_tool.get_job_output(target_id, filter)

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for BashOutput tool."""
        return {
            "name": "BashOutput",
            "description": "Retrieves output from a running or completed background bash job",
            "parameters": {
                "type": "object",
                "properties": {
                    "bash_id": {
                        "type": "string",
                        "description": "The ID of the background job",
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Alias for bash_id",
                    },
                    "id": {
                        "type": "string",
                        "description": "Alias for bash_id",
                    },
                    "filter": {
                        "type": "string",
                        "description": "Optional regex to filter output lines",
                    },
                },
                "required": ["bash_id"],
            },
        }


class KillShell(Tool):
    """Kill a background bash job."""

    def __init__(self, bash_tool: Bash):
        """Initialize KillShell tool.

        Args:
            bash_tool: Reference to Bash tool for accessing jobs
        """
        super().__init__()
        self.bash_tool = bash_tool

    def execute(
        self,
        shell_id: Optional[str] = None,
        bash_id: Optional[str] = None,
        job_id: Optional[str] = None,
        id: Optional[str] = None,
    ) -> ToolResult:
        """Kill a background job.

        Args:
            shell_id: Job ID to kill

        Returns:
            ToolResult
        """
        target_id = shell_id or bash_id or job_id or id
        if not target_id:
            return ToolResult(
                success=False,
                output="",
                error="Missing required parameter 'shell_id'",
            )
        return self.bash_tool.kill_job(target_id)

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for KillShell tool."""
        return {
            "name": "KillShell",
            "description": "Kills a running background bash job by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "shell_id": {
                        "type": "string",
                        "description": "The ID of the background job to kill",
                    },
                    "bash_id": {
                        "type": "string",
                        "description": "Alias for shell_id",
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Alias for shell_id",
                    },
                    "id": {
                        "type": "string",
                        "description": "Alias for shell_id",
                    },
                },
                "required": ["shell_id"],
            },
        }
