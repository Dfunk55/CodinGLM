"""File operation tools: Read, Write, Edit, Glob, Grep."""

import glob
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .base import Tool, ToolResult


class Read(Tool):
    """Read a file from the filesystem."""

    def execute(
        self,
        path: Optional[str] = None,
        file_path: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> ToolResult:
        """Read file contents.

        Args:
            path: Absolute path to file (preferred)
            file_path: Legacy alias for path
            offset: Line number to start from (1-indexed)
            limit: Number of lines to read

        Returns:
            ToolResult with file contents
        """
        try:
            target_path = path or file_path
            if not target_path:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'path'",
                )

            path_obj = Path(target_path).expanduser()

            if not path_obj.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {target_path}",
                )

            if path_obj.is_dir():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Path is a directory: {target_path}",
                )

            # Read file
            with open(path_obj, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # Apply offset and limit
            if offset is not None:
                lines = lines[offset - 1 :]  # Convert to 0-indexed
            if limit is not None:
                lines = lines[:limit]

            # Format with line numbers (cat -n style)
            output_lines = []
            start_line = offset if offset else 1
            for i, line in enumerate(lines, start=start_line):
                # Truncate long lines
                if len(line) > 2000:
                    line = line[:2000] + "... [truncated]\n"
                output_lines.append(f"{i:6}\t{line.rstrip()}")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Read tool."""
        return {
            "name": "Read",
            "description": "Reads a file from the local filesystem with optional line offset and limit",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or project-relative path to the file to read",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "(Legacy) Alias for path",
                    },
                    "offset": {
                        "type": "number",
                        "description": "The line number to start reading from (1-indexed)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "The number of lines to read",
                    },
                },
                "required": ["path"],
            },
        }


class Write(Tool):
    """Write a file to the filesystem."""

    def execute(
        self,
        path: Optional[str] = None,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        contents: Optional[str] = None,
    ) -> ToolResult:
        """Write content to file.

        Args:
            path: Absolute path to file (preferred)
            file_path: Legacy alias for path
            content: Content to write (preferred)
            contents: Alias for content

        Returns:
            ToolResult
        """
        try:
            target_path = path or file_path
            if not target_path:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'path'",
                )

            data = content if content is not None else contents
            if data is None:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'content'",
                )

            path_obj = Path(target_path).expanduser()

            # Create parent directories if needed
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path_obj, "w", encoding="utf-8") as f:
                f.write(data)

            return ToolResult(
                success=True,
                output=f"File written successfully: {target_path}",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Write tool."""
        return {
            "name": "Write",
            "description": "Writes a file to the local filesystem, creating parent directories if needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or project-relative path to the file to write",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "(Legacy) Alias for path",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                    "contents": {
                        "type": "string",
                        "description": "(Legacy) Alias for content",
                    },
                },
                "required": ["path", "content"],
            },
        }


class Edit(Tool):
    """Edit a file by replacing a string."""

    def execute(
        self,
        path: Optional[str] = None,
        file_path: Optional[str] = None,
        old_string: Optional[str] = None,
        new_string: Optional[str] = None,
        match: Optional[str] = None,
        replacement: Optional[str] = None,
        replace_all: bool = False,
    ) -> ToolResult:
        """Edit file by replacing old_string with new_string.

        Args:
            path: Absolute path to file (preferred)
            file_path: Legacy alias for path
            old_string: String to replace
            new_string: Replacement string
            match: Alias for old_string
            replacement: Alias for new_string
            replace_all: Replace all occurrences (default: False)

        Returns:
            ToolResult
        """
        try:
            target_path = path or file_path
            if not target_path:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'path'",
                )

            target_old = old_string if old_string is not None else match
            target_new = new_string if new_string is not None else replacement

            if target_old is None:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'old_string'",
                )

            if target_new is None:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'new_string'",
                )

            path_obj = Path(target_path).expanduser()

            if not path_obj.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {target_path}",
                )

            # Read file
            with open(path_obj, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if old_string exists
            if target_old not in content:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"String not found in file: {target_old[:100]}...",
                )

            # Check if replacement is unique (unless replace_all)
            if not replace_all and content.count(target_old) > 1:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"String appears {content.count(target_old)} times. Use replace_all=true or provide more context.",
                )

            # Perform replacement
            if replace_all:
                new_content = content.replace(target_old, target_new)
            else:
                new_content = content.replace(target_old, target_new, 1)

            # Write back
            with open(path_obj, "w", encoding="utf-8") as f:
                f.write(new_content)

            count = content.count(target_old)
            return ToolResult(
                success=True,
                output=f"Replaced {count if replace_all else 1} occurrence(s) in {target_path}",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Edit tool."""
        return {
            "name": "Edit",
            "description": "Performs exact string replacements in files",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or project-relative path to the file to modify",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "(Legacy) Alias for path",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The text to replace",
                    },
                    "match": {
                        "type": "string",
                        "description": "(Legacy) Alias for old_string",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The text to replace it with",
                    },
                    "replacement": {
                        "type": "string",
                        "description": "(Legacy) Alias for new_string",
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "Replace all occurrences (default false)",
                        "default": False,
                    },
                },
                "required": ["path", "old_string", "new_string"],
            },
        }


class Glob(Tool):
    """Find files matching a glob pattern."""

    def execute(
        self,
        pattern: Optional[str] = None,
        path: Optional[str] = None,
        patterns: Optional[str] = None,
        glob: Optional[str] = None,
        directory: Optional[str] = None,
        recursive: Optional[bool] = None,
    ) -> ToolResult:
        """Find files matching pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            path: Directory to search in (default: current directory)

        Returns:
            ToolResult with matching files
        """
        try:
            resolved_pattern = pattern or glob or patterns
            if not resolved_pattern:
                return ToolResult(
                    success=False,
                    output="",
                    error="Missing required parameter 'pattern'",
                )

            search_root = directory or path
            search_path = Path(search_root).expanduser() if search_root else Path.cwd()

            if not search_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Directory not found: {search_root}",
                )

            # Find matching files
            glob_fn = search_path.glob if recursive is None else search_path.rglob
            matches = list(glob_fn(resolved_pattern))

            # Sort by modification time (most recent first)
            matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            # Format output
            output_lines = [str(p) for p in matches]

            return ToolResult(
                success=True,
                output="\n".join(output_lines) if output_lines else "No files found",
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Glob tool."""
        return {
            "name": "Glob",
            "description": "Fast file pattern matching tool that finds files by glob patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The glob pattern to match files against (e.g., '**/*.py')",
                    },
                    "patterns": {
                        "type": "string",
                        "description": "Optional alias for pattern",
                    },
                    "glob": {
                        "type": "string",
                        "description": "Optional alias for pattern",
                    },
                    "path": {
                        "type": "string",
                        "description": "The directory to search in (defaults to current directory)",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Optional alias for path",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Set to true to search recursively (uses rglob)",
                    },
                },
                "required": ["pattern"],
            },
        }


class Grep(Tool):
    """Search for text patterns in files using ripgrep."""

    def execute(
        self,
        pattern: str,
        path: Optional[str] = None,
        glob: Optional[str] = None,
        output_mode: str = "files_with_matches",
        case_insensitive: bool = False,
        context_lines: int = 0,
    ) -> ToolResult:
        """Search for pattern in files.

        Args:
            pattern: Regex pattern to search for
            path: File or directory to search in
            glob: Glob pattern to filter files
            output_mode: "files_with_matches", "content", or "count"
            case_insensitive: Case insensitive search
            context_lines: Lines of context to show

        Returns:
            ToolResult with search results
        """
        try:
            # Build ripgrep command
            cmd = ["rg"]

            if case_insensitive:
                cmd.append("-i")

            if output_mode == "files_with_matches":
                cmd.append("-l")
            elif output_mode == "count":
                cmd.append("-c")

            if context_lines > 0:
                cmd.extend(["-C", str(context_lines)])

            if glob:
                cmd.extend(["--glob", glob])

            cmd.append(pattern)

            if path:
                cmd.append(path)

            # Run ripgrep
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                return ToolResult(
                    success=True,
                    output=output if output else "No matches found",
                )
            elif result.returncode == 1:
                # No matches found
                return ToolResult(
                    success=True,
                    output="No matches found",
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=result.stderr,
                )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                output="",
                error="ripgrep (rg) not found. Install with: brew install ripgrep",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for Grep tool."""
        return {
            "name": "Grep",
            "description": "Search for text patterns in files using ripgrep",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The regular expression pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in (defaults to current directory)",
                    },
                    "glob": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g., '*.py')",
                    },
                    "output_mode": {
                        "type": "string",
                        "enum": ["files_with_matches", "content", "count"],
                        "description": "Output mode: files_with_matches (default), content, or count",
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Case insensitive search",
                    },
                    "context_lines": {
                        "type": "number",
                        "description": "Number of context lines to show",
                    },
                },
                "required": ["pattern"],
            },
        }
