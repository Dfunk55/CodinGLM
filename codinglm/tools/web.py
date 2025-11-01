"""Web tools: WebSearch and WebFetch."""

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Any, Dict, Optional
from .base import Tool, ToolResult


class WebSearch(Tool):
    """Search the web (requires external API - placeholder implementation)."""

    def execute(self, query: str) -> ToolResult:
        """Search the web for query.

        Args:
            query: Search query

        Returns:
            ToolResult with search results
        """
        # NOTE: This is a placeholder. In production, you would integrate with:
        # - Google Custom Search API
        # - Bing Search API
        # - DuckDuckGo API
        # - Or use Z.ai's web search MCP if available

        return ToolResult(
            success=False,
            output="",
            error="WebSearch not implemented. Use WebFetch for specific URLs or configure web search MCP.",
        )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for WebSearch tool."""
        return {
            "name": "WebSearch",
            "description": "Search the web and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                },
                "required": ["query"],
            },
        }


class WebFetch(Tool):
    """Fetch and process web content."""

    def execute(self, url: str, prompt: str) -> ToolResult:
        """Fetch URL and process with prompt.

        Args:
            url: URL to fetch
            prompt: What information to extract

        Returns:
            ToolResult with processed content
        """
        try:
            # Upgrade to HTTPS if needed
            if url.startswith("http://"):
                url = url.replace("http://", "https://", 1)

            # Fetch URL
            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()

            # Check for redirects to different host
            if response.url.host != httpx.URL(url).host:
                return ToolResult(
                    success=True,
                    output=f"Redirected to different host: {response.url}\nPlease fetch: {response.url}",
                )

            # Parse HTML to markdown
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Convert to markdown
            markdown_content = md(str(soup))

            # Truncate if too long
            if len(markdown_content) > 10000:
                markdown_content = markdown_content[:10000] + "\n\n... [content truncated]"

            # Add context about the prompt
            output = f"# Content from {url}\n\n"
            output += f"**Extraction prompt:** {prompt}\n\n"
            output += markdown_content

            return ToolResult(
                success=True,
                output=output,
            )

        except httpx.HTTPStatusError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"HTTP error: {e.response.status_code}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for WebFetch tool."""
        return {
            "name": "WebFetch",
            "description": "Fetches content from a URL and processes it",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch content from",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "What information to extract from the page",
                    },
                },
                "required": ["url", "prompt"],
            },
        }
