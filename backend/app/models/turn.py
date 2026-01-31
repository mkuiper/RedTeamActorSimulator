"""Turn model for individual dialog turns in a simulation."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.objective import Objective
    from app.models.session import Session


class Turn(Base):
    """Individual dialog turn in a simulation."""

    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Parent references
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), nullable=False
    )
    objective_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("objectives.id"), nullable=False
    )

    # Turn ordering within the objective
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Actor (persona) message
    actor_message: Mapped[str] = mapped_column(Text, nullable=False)

    # Actor's chain-of-thought (if available, shows reasoning process)
    actor_thinking: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Subject (model being tested) response
    subject_response: Mapped[str] = mapped_column(Text, nullable=False)

    # Subject's chain-of-thought (if available, for sneaky mode)
    subject_thinking: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Assessor evaluation
    assessor_evaluation: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Quick-access fields from evaluation
    criteria_met: Mapped[bool] = mapped_column(Boolean, default=False)
    refusal_detected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Strategy tracking
    actor_strategy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="turns")
    objective: Mapped["Objective"] = relationship("Objective", back_populates="turns")

    def __repr__(self) -> str:
        return f"<Turn(id={self.id}, turn_number={self.turn_number}, criteria_met={self.criteria_met})>"
