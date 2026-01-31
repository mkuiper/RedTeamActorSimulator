"""Web search tool implementation."""

import logging
from typing import Any, Dict, Optional

import httpx

from app.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """Tool for performing web searches."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize web search tool.

        Config options:
            - api_key: Search API key (e.g., SerpAPI, Brave Search)
            - engine: Search engine to use (default: "serpapi")
            - max_results: Maximum results to return (default: 5)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        self.engine = self.config.get("engine", "serpapi")
        self.max_results = self.config.get("max_results", 5)

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for information. Useful for finding current information, facts, or research."

    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        }

    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        """
        Execute a web search.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            ToolResult with search results
        """
        if not self.api_key:
            return ToolResult(
                success=False,
                output="",
                error="Web search not configured (missing API key)",
            )

        try:
            if self.engine == "serpapi":
                results = await self._search_serpapi(query, num_results)
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unsupported search engine: {self.engine}",
                )

            # Format results
            formatted = self._format_results(results)

            return ToolResult(
                success=True,
                output=formatted,
                metadata={"num_results": len(results), "query": query},
            )

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Search failed: {str(e)}",
            )

    async def _search_serpapi(self, query: str, num_results: int) -> list:
        """Search using SerpAPI."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://serpapi.com/search",
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": num_results,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            return data.get("organic_results", [])

    def _format_results(self, results: list) -> str:
        """Format search results for display."""
        if not results:
            return "No results found."

        formatted = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description")
            link = result.get("link", "")

            formatted.append(f"{i}. {title}\n{snippet}\nURL: {link}")

        return "\n\n".join(formatted)
