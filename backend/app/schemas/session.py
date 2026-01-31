"""Session-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.session import SessionStatus


class AgentToolConfig(BaseModel):
    """Configuration for tools available to an agent."""

    web_search: bool = Field(default=False, description="Enable web search capability")
    code_execution: bool = Field(default=False, description="Enable code execution")
    mcp_servers: List[str] = Field(default_factory=list, description="MCP server names to connect")
    file_access: bool = Field(default=False, description="Enable file system access")


class ToolConfig(BaseModel):
    """Tool configuration for all agents in a session."""

    actor: Optional[AgentToolConfig] = Field(default=None, description="Tools for actor agent")
    assessor: Optional[AgentToolConfig] = Field(default=None, description="Tools for assessor agent")


class SessionCreate(BaseModel):
    """Schema for creating a new session."""

    name: str = Field(..., min_length=1, max_length=255)
    max_turns: int = Field(default=20, ge=1, le=100)
    sneaky_mode: bool = False

    # Model configuration (provider:model format)
    actor_model: str = Field(..., description="Actor agent model (e.g., 'anthropic:claude-3-5-sonnet')")
    assessor_model: str = Field(..., description="Assessor agent model")
    subject_model: str = Field(..., description="Subject model being tested")

    # Tool configuration
    tool_config: Optional[ToolConfig] = Field(default=None, description="Tool configuration for agents")

    # Persona reference
    persona_id: str = Field(..., description="ID of the persona to use")

    # Objectives
    objectives: List["ObjectiveCreate"] = Field(..., min_length=1)


class SessionUpdate(BaseModel):
    """Schema for updating a session."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[SessionStatus] = None


class SessionResponse(BaseModel):
    """Schema for session response."""

    id: str
    name: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    max_turns: int
    sneaky_mode: bool
    actor_model: str
    assessor_model: str
    subject_model: str
    tool_config: Optional[Dict[str, Any]] = None
    persona_id: str
    config_json: Dict[str, Any]
    final_report_md: Optional[str] = None
    objectives: List["ObjectiveResponse"] = []
    turns: List["TurnResponse"] = []

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Schema for listing sessions."""

    sessions: List[SessionResponse]
    total: int


# Forward references
from app.schemas.objective import ObjectiveCreate, ObjectiveResponse  # noqa: E402
from app.schemas.turn import TurnResponse  # noqa: E402

SessionCreate.model_rebuild()
SessionResponse.model_rebuild()
