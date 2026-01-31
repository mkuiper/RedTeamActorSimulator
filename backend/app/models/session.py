"""Session model for simulation sessions."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.objective import Objective
    from app.models.turn import Turn


class SessionStatus(str, enum.Enum):
    """Status of a simulation session."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


class Session(Base):
    """Simulation session model."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.PENDING
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Configuration snapshot (stores full config at session creation)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Final report (generated upon completion)
    final_report_md: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Session settings
    max_turns: Mapped[int] = mapped_column(default=20)
    sneaky_mode: Mapped[bool] = mapped_column(default=False)

    # Model configuration
    actor_model: Mapped[str] = mapped_column(String(100), nullable=False)
    assessor_model: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Tool configuration for agents
    # Format: {"actor": {"web_search": true, "mcp_servers": ["server1"]}, "assessor": {...}}
    tool_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    # Persona reference
    persona_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    objectives: Mapped[List["Objective"]] = relationship(
        "Objective", back_populates="session", cascade="all, delete-orphan"
    )
    turns: Mapped[List["Turn"]] = relationship(
        "Turn", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, name={self.name}, status={self.status})>"
