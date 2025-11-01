# search-aggregator-mcp

Unified search MCP server that fans out queries to multiple providers (Tavily, Exa, Brave, Bing, SerpAPI/Google) and aggregates, deduplicates, and optionally reranks results.

## Features
- Provider-agnostic `search` tool with normalized results
- Automatic provider selection based on available API keys
- Optional reranking via Cohere ReRank if `COHERE_API_KEY` is set
- Configurable limits, time range, site filters

## Env Vars
- `TAVILY_API_KEY`
- `EXA_API_KEY`
- `BRAVE_API_KEY`
- `BING_API_KEY`
- `SERPAPI_KEY`
- `KAGI_API_KEY` (reserved)
- `COHERE_API_KEY` (optional rerank)

## Run
```
cd mcp-servers/javascript/search-aggregator-mcp
npm install
node index.js
```
