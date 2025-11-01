"""Tests for GLM API client helpers."""

import json

from codinglm.api.client import GLMClient
from codinglm.api.models import Message, ToolDefinition


def _make_client() -> GLMClient:
    return GLMClient(api_key="dummy-key", model="glm-4.6", base_url="https://example.com")


def test_build_payload_converts_messages_with_tools():
    client = _make_client()
    messages = [
        Message(role="system", content="sys prompt"),
        Message(role="user", content="hi"),
        Message(
            role="assistant",
            content=None,
            tool_calls=[
                {
                    "id": "toolu_1",
                    "function": {
                        "name": "Read",
                        "arguments": '{"path": "foo.txt"}',
                    },
                }
            ],
        ),
        Message(role="tool", content="file content", tool_call_id="toolu_1"),
    ]

    payload = client._build_payload(messages, tools=None)

    assert payload["system"] == "sys prompt"
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][1]["role"] == "assistant"
    tool_use = payload["messages"][1]["content"][0]
    assert tool_use["type"] == "tool_use"
    assert tool_use["name"] == "Read"
    assert tool_use["input"]["path"] == "foo.txt"

    tool_result = payload["messages"][2]["content"][0]
    assert tool_result["type"] == "tool_result"
    assert tool_result["tool_use_id"] == "toolu_1"
    assert tool_result["content"] == "file content"


def test_tool_to_anthropic_conversion():
    client = _make_client()
    tool = ToolDefinition(
        function={
            "name": "Read",
            "description": "Read a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        }
    )

    converted = client._tool_to_anthropic(tool)
    assert converted["type"] == "tool"
    assert converted["name"] == "Read"
    assert converted["description"] == "Read a file"
    assert converted["input_schema"]["required"] == ["path"]


def test_tool_to_anthropic_accepts_plain_dict():
    client = _make_client()
    tool = {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write a file",
            "parameters": '{"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}',
        },
    }

    converted = client._tool_to_anthropic(tool)
    assert converted["name"] == "Write"
    assert converted["input_schema"]["required"] == ["path"]


def test_parse_event_stream_accumulates_tool_arguments():
    client = _make_client()

    lines = [
        "event: content_block_start",
        'data: {"index": 0, "content_block": {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {}}}',
        "event: content_block_delta",
        'data: {"index": 0, "delta": {"type": "input_json_delta", "partial_json": "{\\"command\\":\\"ls\\"}"}}',
        "event: content_block_stop",
        'data: {"index": 0}',
        "event: message_stop",
        'data: {"stop_reason": "tool_use"}',
        "data: [DONE]",
    ]

    class FakeResponse:
        def __init__(self, raw_lines):
            self._raw_lines = raw_lines

        def iter_lines(self):
            for entry in self._raw_lines:
                yield entry

    chunks = list(client._parse_event_stream(FakeResponse(lines)))
    tool_chunks = [chunk for chunk in chunks if chunk.tool_calls]
    assert len(tool_chunks) == 1

    call = tool_chunks[0].tool_calls[0]
    assert call.function["name"] == "Bash"
    assert json.loads(call.function["arguments"]) == {"command": "ls"}
