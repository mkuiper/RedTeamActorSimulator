"""Tool manager for coordinating agent tool use."""

import logging
from typing import Any, Dict, List, Optional

from app.tools.base import Tool, ToolResult
from app.tools.code_executor import CodeExecutorTool
from app.tools.mcp_client import MCPClientTool
from app.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class ToolManager:
    """Manages tools available to an agent."""

    def __init__(self, tool_config: Optional[Dict[str, Any]] = None):
        """
        Initialize tool manager.

        Args:
            tool_config: Configuration dict with tool settings
                Example: {
                    "web_search": True,
                    "code_execution": True,
                    "mcp_servers": [{"name": "fs", "command": "..."}]
                }
        """
        self.tool_config = tool_config or {}
        self.tools: Dict[str, Tool] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize tools based on configuration."""
        # Web search
        if self.tool_config.get("web_search", False):
            search_config = {
                "api_key": self.tool_config.get("web_search_api_key"),
                "engine": self.tool_config.get("search_engine", "serpapi"),
            }
            self.tools["web_search"] = WebSearchTool(search_config)
            logger.info("Initialized web search tool")

        # Code execution
        if self.tool_config.get("code_execution", False):
            code_config = {
                "timeout": self.tool_config.get("code_timeout", 30),
                "allowed_languages": self.tool_config.get("allowed_languages", ["python"]),
            }
            self.tools["code_executor"] = CodeExecutorTool(code_config)
            logger.info("Initialized code executor tool")

        # MCP servers
        mcp_servers = self.tool_config.get("mcp_servers", [])
        if mcp_servers:
            mcp_config = {"servers": mcp_servers}
            self.tools["mcp_client"] = MCPClientTool(mcp_config)
            logger.info(f"Initialized MCP client with {len(mcp_servers)} servers")

    def has_tools(self) -> bool:
        """Check if any tools are available."""
        return len(self.tools) > 0

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get schemas for all available tools.

        Returns:
            List of tool schemas for LLM tool use
        """
        return [tool.get_schema() for tool in self.tools.values()]

    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a specific tool.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with execution outcome
        """
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{tool_name}' not available",
            )

        try:
            tool = self.tools[tool_name]
            result = await tool.execute(**kwargs)
            logger.info(f"Executed tool '{tool_name}': success={result.success}")
            return result
        except Exception as e:
            logger.error(f"Tool execution error for '{tool_name}': {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Tool execution failed: {str(e)}",
            )

    def get_tool_descriptions(self) -> str:
        """
        Get a formatted string describing all available tools.

        Returns:
            Formatted tool descriptions for prompt inclusion
        """
        if not self.tools:
            return "No tools available."

        descriptions = []
        for tool in self.tools.values():
            schema = tool.get_schema()
            params = schema.get("parameters", {})
            props = params.get("properties", {})

            param_desc = []
            for param_name, param_info in props.items():
                required = param_name in params.get("required", [])
                param_desc.append(
                    f"  - {param_name} ({'required' if required else 'optional'}): {param_info.get('description', '')}"
                )

            descriptions.append(
                f"**{tool.name}**: {tool.description}\n"
                + "Parameters:\n"
                + "\n".join(param_desc)
            )

        return "\n\n".join(descriptions)

    async def cleanup(self):
        """Clean up resources used by tools."""
        if "mcp_client" in self.tools:
            mcp_tool = self.tools["mcp_client"]
            if isinstance(mcp_tool, MCPClientTool):
                await mcp_tool.disconnect_all()
        logger.info("Cleaned up tool manager resources")
