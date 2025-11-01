"""Tests for MCP client."""

import pytest

from codinglm.mcp.client import MCPClientManager
from codinglm.config import MCPServerConfig


def test_mcp_manager_initialization():
    """Test MCPClientManager can be instantiated."""
    manager = MCPClientManager()
    assert manager is not None
    assert manager.servers == {}
    assert manager.available_servers == {}


def test_register_server():
    """Test server registration."""
    manager = MCPClientManager()

    config = MCPServerConfig(
        command="node",
        args=["test.js"],
        env={}
    )

    manager.register_server("test-server", config)

    assert "test-server" in manager.available_servers
    assert manager.available_servers["test-server"] == config
    assert "test-server" not in manager.servers  # Not enabled yet


def test_list_servers():
    """Test listing available and enabled servers."""
    manager = MCPClientManager()

    config1 = MCPServerConfig(command="node", args=["test1.js"], env={})
    config2 = MCPServerConfig(command="node", args=["test2.js"], env={})

    manager.register_server("server1", config1)
    manager.register_server("server2", config2)

    available = manager.get_available_servers()
    assert len(available) == 2
    assert "server1" in available
    assert "server2" in available

    enabled = manager.get_enabled_servers()
    assert len(enabled) == 0  # None enabled yet


def test_get_all_tools_empty():
    """Test getting tools when no servers are enabled."""
    manager = MCPClientManager()

    config = MCPServerConfig(command="node", args=["test.js"], env={})
    manager.register_server("test-server", config)

    tools = manager.get_all_tools()
    assert tools == []


# Note: We can't easily test actual server connection without mocking
# the asyncio connection process, which would require more complex setup.
# The above tests verify the basic client infrastructure works.
