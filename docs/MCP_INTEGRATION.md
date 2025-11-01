# MCP Integration Guide

CodinGLM supports the Model Context Protocol (MCP) for extensible tool integration. MCP servers can be dynamically loaded and unloaded during a conversation to manage context usage efficiently.

## Features

- **Dynamic Loading**: Enable/disable MCP servers on-demand during conversations
- **Context-Efficient**: Only load servers when needed to avoid wasting tokens
- **Runtime Management**: Use `/mcp` commands to control which servers are active
- **Tool Namespacing**: MCP tools are prefixed with `mcp::servername::toolname` to avoid conflicts

## Configuration

MCP servers are configured in your `.codinglm.json` file:

```json
{
  "mcpServers": {
    "browser-automation": {
      "command": "npx",
      "args": ["-y", "@automatalabs/mcp-server-playwright"]
    },
    "shell": {
      "command": "uvx",
      "args": ["mcp-server-shell"]
    },
    "search-aggregator": {
      "command": "node",
      "args": ["mcp_servers/search-aggregator/index.js"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}",
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "testing-toolbox": {
      "command": "node",
      "args": ["mcp_servers/testing-toolbox/index.js"],
      "env": {}
    }
  }
}
```

### Configuration Options

- `command`: The executable to run (e.g., `node`, `python3`, `npx`, `uvx`)
- `args`: Array of command-line arguments
- `env`: Optional environment variables (supports `${VAR}` substitution)

## Usage

### List Available Servers

```
/mcp list
```

Shows all configured servers with `[x]` indicating enabled servers.

Example output:
```
Available MCP servers:
  [ ] browser-automation
  [ ] shell
  [x] search-aggregator (enabled)
  [ ] testing-toolbox
```

### Enable a Server

```
/mcp enable search-aggregator
```

Connects to the server and loads its tools into the conversation. You'll see confirmation with the tool count:

```
✓ Enabled MCP server 'search-aggregator' (3 tools)
```

### Disable a Server

```
/mcp disable search-aggregator
```

Disconnects from the server and removes its tools:

```
✓ Disabled MCP server 'search-aggregator'
```

### Check Status

```
/mcp status
```

Shows currently active servers and total tool count:

```
Active MCP servers: search-aggregator, testing-toolbox
Total MCP tools: 8
```

## Built-in MCP Servers

CodinGLM includes two MCP servers in the `mcp_servers/` directory:

### search-aggregator

Multi-provider web search aggregator supporting:
- Tavily (requires `TAVILY_API_KEY`)
- Brave (requires `BRAVE_API_KEY`)
- Bing (requires `BING_API_KEY`)
- Exa (requires `EXA_API_KEY`)
- SerpAPI (requires `SERPAPI_KEY`)

**Tools:**
- `search` - Search across configured providers
- `config` - Show available search providers

### testing-toolbox

Testing framework integration for Python, JavaScript, Rust, and Go:

**Tools:**
- `test_discover` - Discover tests in a project
- `test_run` - Run tests with coverage
- `test_watch` - Watch mode for continuous testing
- `mutation_test` - Mutation testing
- `fuzz_test` - Fuzz testing

**Note:** Requires the toolbox binary at `/Users/dustinpainter/Dev-Projects/toolbox/rust-workspace/target/debug/toolbox`

## Best Practices

### Context Management

Only enable servers when you need their tools:

```
# Good: Enable search when you need to research
/mcp enable search-aggregator
Please search for the latest React 19 features

# Good: Disable when done to save context
/mcp disable search-aggregator
```

### Typical Workflow

1. Start conversation with core tools only
2. Enable specific MCP servers as needed for the task
3. Disable servers after completing their related work
4. Use `/mcp status` to monitor active servers

### Context Savings

Example context usage with 4 servers configured but only 1 enabled:

- All 4 enabled: ~30,000 tokens
- 1 enabled: ~3,000 tokens
- None enabled: ~0 tokens

This allows you to have 20+ servers configured without wasting context.

## Adding Custom MCP Servers

### Option 1: External Package

Add any MCP-compatible server via package managers:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@org/my-mcp-server"]
    }
  }
}
```

### Option 2: Local Server

Place your MCP server in `mcp_servers/my-server/`:

```
mcp_servers/
└── my-server/
    ├── index.js          # Entry point
    ├── package.json      # Dependencies
    └── mcp-server.json   # Metadata
```

Then configure it:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["mcp_servers/my-server/index.js"],
      "env": {}
    }
  }
}
```

## Troubleshooting

### Server Won't Connect

1. Verify the command/args are correct
2. Check that dependencies are installed (e.g., `npm install` in server directory)
3. Ensure environment variables are set
4. Check server logs in terminal output

### Tools Not Showing Up

1. Use `/mcp status` to verify server is enabled
2. Use `/tools` to see all available tools (including MCP)
3. Check that the server is actually running (no errors during enable)

### High Context Usage

1. Use `/mcp list` to see which servers are enabled
2. Disable unused servers with `/mcp disable <name>`
3. Use `/mcp status` to monitor total tool count

## Technical Details

### Tool Naming Convention

MCP tools are prefixed to avoid name conflicts:

- Original: `search`
- In CodinGLM: `mcp::search-aggregator::search`

The prefix format is `mcp::{server_name}::{tool_name}`. The `::` separator is used instead of `_` to support server and tool names that contain underscores.

### Connection Lifecycle

1. Server registered in config → Available for enabling
2. `/mcp enable` → Spawns server process, connects via stdio
3. Server provides tool list → Tools added to registry
4. `/mcp disable` → Disconnects from server, removes tools
5. Server process terminated

### Async Architecture

MCP operations use Python's `asyncio`:

```python
# In CLI handler
import asyncio
asyncio.run(manager.enable_server("search-aggregator"))
```

The conversation manager maintains the MCP client manager instance for the session.
