"""MCP client for managing connections to MCP servers."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Optional

from mcp import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from mcp.types import Tool

from ..config import MCPServerConfig

logger = logging.getLogger(__name__)


class MCPServerConnection:
    """Represents a connection to an MCP server."""

    def __init__(self, name: str, config: MCPServerConfig):
        """Initialize MCP server connection.

        Args:
            name: Server name
            config: Server configuration
        """
        self.name = name
        self.config = config
        self.session: Optional[ClientSession] = None
        self.tools: List[Tool] = []
        self._read_stream = None
        self._write_stream = None
        self._stdio_context = None
        self._session_context = None

    async def connect(self) -> bool:
        """Connect to the MCP server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            server_params = StdioServerParameters(
                command=self.config.command,
                args=self.config.args,
                env=self.config.env if self.config.env else None,
            )

            # Create and enter stdio context
            self._stdio_context = stdio_client(server_params)
            self._read_stream, self._write_stream = await self._stdio_context.__aenter__()

            # Create and enter session context
            self._session_context = ClientSession(self._read_stream, self._write_stream)
            await self._session_context.__aenter__()
            self.session = self._session_context

            # List available tools
            result = await self.session.list_tools()
            self.tools = result.tools

            logger.info(f"Connected to MCP server '{self.name}' with {len(self.tools)} tools")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{self.name}': {e}")
            # Clean up on failure
            await self._cleanup_contexts()
            return False

    async def _cleanup_contexts(self):
        """Clean up context managers."""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
                self._session_context = None
        except Exception as e:
            logger.error(f"Error cleaning up session context: {e}")

        try:
            if self._stdio_context:
                await self._stdio_context.__aexit__(None, None, None)
                self._stdio_context = None
        except Exception as e:
            logger.error(f"Error cleaning up stdio context: {e}")

    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            await self._cleanup_contexts()
            self.session = None
            self.tools = []
            self._read_stream = None
            self._write_stream = None
            logger.info(f"Disconnected from MCP server '{self.name}'")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server '{self.name}': {e}")

    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if not self.session:
            raise RuntimeError(f"Not connected to MCP server '{self.name}'")

        result = await self.session.call_tool(tool_name, arguments)
        return result


class MCPClientManager:
    """Manages MCP server connections and tool availability."""

    def __init__(self):
        """Initialize MCP client manager."""
        self.servers: Dict[str, MCPServerConnection] = {}
        self.available_servers: Dict[str, MCPServerConfig] = {}

    def register_server(self, name: str, config: MCPServerConfig):
        """Register an available MCP server.

        Args:
            name: Server name
            config: Server configuration
        """
        self.available_servers[name] = config
        logger.info(f"Registered MCP server '{name}'")

    async def enable_server(self, name: str) -> bool:
        """Enable and connect to an MCP server.

        Args:
            name: Server name

        Returns:
            True if enabled successfully, False otherwise
        """
        if name in self.servers:
            logger.warning(f"MCP server '{name}' already enabled")
            return True

        if name not in self.available_servers:
            logger.error(f"MCP server '{name}' not registered")
            return False

        config = self.available_servers[name]
        connection = MCPServerConnection(name, config)

        if await connection.connect():
            self.servers[name] = connection
            return True
        return False

    async def disable_server(self, name: str) -> bool:
        """Disable and disconnect from an MCP server.

        Args:
            name: Server name

        Returns:
            True if disabled successfully, False otherwise
        """
        if name not in self.servers:
            logger.warning(f"MCP server '{name}' not enabled")
            return False

        connection = self.servers.pop(name)
        await connection.disconnect()
        return True

    def get_enabled_servers(self) -> List[str]:
        """Get list of enabled server names.

        Returns:
            List of enabled server names
        """
        return list(self.servers.keys())

    def get_available_servers(self) -> List[str]:
        """Get list of available server names.

        Returns:
            List of available server names
        """
        return list(self.available_servers.keys())

    def get_all_tools(self) -> List[Dict]:
        """Get all tools from enabled servers.

        Returns:
            List of tool definitions
        """
        tools = []
        for server_name, connection in self.servers.items():
            for tool in connection.tools:
                # Convert MCP tool to function definition format
                # Use :: separator to avoid conflicts with underscores in names
                tools.append({
                    "name": f"mcp::{server_name}::{tool.name}",
                    "description": f"[{server_name}] {tool.description}",
                    "parameters": tool.inputSchema,
                    "_mcp_server": server_name,
                    "_mcp_tool": tool.name,
                })
        return tools

    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call an MCP tool.

        Args:
            tool_name: Tool name (format: mcp::servername::toolname)
            arguments: Tool arguments

        Returns:
            Tool result
        """
        # Parse server and tool name
        if not tool_name.startswith("mcp::"):
            raise ValueError(f"Invalid MCP tool name: {tool_name}")

        parts = tool_name[5:].split("::", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid MCP tool name format: {tool_name}")

        server_name, original_tool_name = parts

        if server_name not in self.servers:
            raise RuntimeError(f"MCP server '{server_name}' not enabled")

        connection = self.servers[server_name]
        return await connection.call_tool(original_tool_name, arguments)

    async def shutdown(self):
        """Shutdown all MCP connections."""
        for name in list(self.servers.keys()):
            await self.disable_server(name)
