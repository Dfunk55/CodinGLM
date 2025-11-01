# CodinGLM

A fully-featured Claude Code clone powered by Z.ai's GLM models, designed to leverage Z.ai's subscription usage plan.

## Features

- **Full tool support**: File operations, bash execution, git integration, web search/fetch
- **Task management**: Built-in TodoWrite for tracking complex tasks
- **Agent system**: Spawn sub-agents for complex operations
- **MCP integration**: Extensible via Model Context Protocol servers
- **Rich UI**: Markdown rendering with syntax highlighting
- **Slash commands**: Custom commands and skills
- **Streaming responses**: Real-time output from GLM-4.6

## Installation

```bash
cd CodinGLM
pip install -e .
```

Or with Poetry:

```bash
poetry install
poetry shell
```

## Configuration

Create a `.codinglm.json` file in your project or home directory:

```json
{
  "apiKey": "your-z-ai-api-key",
  "model": "glm-4.6",
  "apiBase": "https://api.z.ai/api/anthropic",
  "apiTimeoutMs": 600000,
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": ["-y", "@automatalabs/mcp-server-playwright"]
    },
    "shell": {
      "command": "uvx",
      "args": ["mcp-server-shell"]
    }
  }
}
```

Or set the API key via environment variable:

```bash
export Z_AI_API_KEY="your-api-key"
# Optionally override API endpoint/timeout
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export API_TIMEOUT_MS="600000"
```

## Usage

```bash
# Start interactive session
codinglm

# With specific working directory
codinglm --cwd /path/to/project

# Use specific model
codinglm --model glm-4.6

# Enable debug logging
codinglm --debug
```

Press `Esc` while a response is streaming to interrupt it.

### Available Commands

- `/help` - Show help message
- `/clear` - Clear conversation history
- `/permissions` - Show tool permissions
- `/model <name>` - Switch the active GLM model
- `/models` - Interactive model selector (arrow keys + Enter)
- `/tools` - Show tool reference with required parameters
- `/mcp list` - List available MCP servers (shows enabled status)
- `/mcp enable <server>` - Enable an MCP server and load its tools
- `/mcp disable <server>` - Disable an MCP server and unload its tools
- `/mcp status` - Show active MCP servers and tool count
- `/exit` - Exit the session

## Architecture

```
codinglm/
├── api/          # Z.ai API client wrapper
├── tools/        # Tool implementations
├── mcp/          # MCP server integration
├── ui/           # CLI interface
├── conversation/ # Conversation management
└── config.py     # Configuration handling
```

## Development

```bash
# Run tests
pytest
# Run just the pseudo-terminal smoke test
pytest tests/integration/test_cli_pty.py

# Format code
black codinglm/
ruff check codinglm/

# Type checking
mypy codinglm/
```

## License

MIT
