"""Tool execution history tracking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ToolHistoryEntry:
    """Captured details about a tool execution."""

    name: str
    call_id: str
    success: bool
    output: str


class ToolHistory:
    """Maintain a bounded history of tool executions."""

    def __init__(self, max_entries: int = 20):
        self._entries: List[ToolHistoryEntry] = []
        self._max_entries = max_entries

    def add(self, entry: ToolHistoryEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)

    def latest(self) -> ToolHistoryEntry | None:
        return self._entries[-1] if self._entries else None

    def get(self, index: int) -> ToolHistoryEntry | None:
        if not self._entries:
            return None
        if index < 0:
            index = len(self._entries) + index
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def all(self) -> List[ToolHistoryEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)
