"""Tests for tool execution history helper."""

from __future__ import annotations

from codinglm.tools.history import ToolHistory, ToolHistoryEntry


def _make_entry(idx: int, success: bool = True) -> ToolHistoryEntry:
    return ToolHistoryEntry(
        name=f"tool-{idx}",
        call_id=f"call-{idx}",
        success=success,
        output=f"output-{idx}",
    )


def test_history_discards_old_entries_when_full():
    history = ToolHistory(max_entries=3)

    for idx in range(5):
        history.add(_make_entry(idx))

    assert len(history) == 3
    remaining_ids = [entry.call_id for entry in history.all()]
    assert remaining_ids == ["call-2", "call-3", "call-4"]
    assert history.latest().call_id == "call-4"


def test_history_supports_indexing_and_negative_lookup():
    history = ToolHistory(max_entries=5)
    for idx in range(3):
        history.add(_make_entry(idx, success=idx % 2 == 0))

    assert history.get(0).call_id == "call-0"
    assert history.get(1).success is False
    assert history.get(-1).call_id == "call-2"
    assert history.get(-2).call_id == "call-1"
    assert history.get(5) is None
    assert history.get(-5) is None


def test_history_clear_removes_all_entries():
    history = ToolHistory(max_entries=2)
    history.add(_make_entry(0))
    history.add(_make_entry(1))
    assert len(history) == 2

    history.clear()

    assert len(history) == 0
    assert history.latest() is None
    assert history.all() == []
