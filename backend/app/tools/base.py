"""Base tool interface for agent tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from a tool execution."""

    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Tool(ABC):
    """Abstract base class for agent tools."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the tool.

        Args:
            config: Tool-specific configuration
        """
        self.config = config or {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with execution outcome
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's parameter schema for LLM tool use.

        Returns:
            JSON schema describing the tool's parameters
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema(),
        }

    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for the tool's parameters.

        Returns:
            JSON schema object
        """
        pass
