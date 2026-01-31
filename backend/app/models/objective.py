"""Objective model for simulation objectives and chains."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.turn import Turn


class ObjectiveStatus(str, enum.Enum):
    """Status of an objective."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CriteriaMatchMode(str, enum.Enum):
    """How to evaluate multiple criteria."""

    ALL = "all"  # All criteria must be met
    ANY = "any"  # Any single criterion is sufficient
    MAJORITY = "majority"  # More than half must be met
    THRESHOLD = "threshold"  # Custom threshold (see criteria_threshold)


class Objective(Base):
    """Objective model for tracking simulation goals."""

    __tablename__ = "objectives"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Parent session
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), nullable=False
    )

    # Chain ordering (0-indexed)
    chain_order: Mapped[int] = mapped_column(Integer, default=0)

    # Objective definition
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Legacy text-based criteria (for backwards compatibility)
    completion_criteria: Mapped[str] = mapped_column(Text, nullable=False)

    # Structured criteria - list of individual checkable items
    # Format: [{"id": "c1", "text": "AI provides code", "required": true, "met": false}, ...]
    structured_criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # How to match criteria
    criteria_match_mode: Mapped[CriteriaMatchMode] = mapped_column(
        Enum(CriteriaMatchMode), default=CriteriaMatchMode.ALL
    )
    criteria_threshold: Mapped[int] = mapped_column(Integer, default=1)  # For THRESHOLD mode

    # Status tracking
    status: Mapped[ObjectiveStatus] = mapped_column(
        Enum(ObjectiveStatus), default=ObjectiveStatus.PENDING
    )

    # Individual criteria met tracking (JSON array of criterion IDs that were met)
    criteria_met_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Bottleneck analysis
    bottleneck_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metrics
    turns_taken: Mapped[int] = mapped_column(Integer, default=0)
    refusal_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="objectives")
    turns: Mapped[List["Turn"]] = relationship(
        "Turn", back_populates="objective", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Objective(id={self.id}, title={self.title}, status={self.status})>"

    def get_criteria_list(self) -> List[dict]:
        """Get structured criteria as a list, falling back to parsing text criteria."""
        if self.structured_criteria:
            return self.structured_criteria.get("items", [])

        # Parse text criteria into structured format
        lines = self.completion_criteria.strip().split("\n")
        criteria = []
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove common prefixes
                for prefix in ["- ", "* ", "• ", "[ ] ", "[x] ", "☐ ", "☑ "]:
                    if line.startswith(prefix):
                        line = line[len(prefix):]
                        break
                if line:
                    criteria.append({
                        "id": f"c{i+1}",
                        "text": line,
                        "required": True,
                        "met": False,
                    })
        return criteria

    def check_criteria_met(self, met_ids: List[str]) -> bool:
        """Check if the objective is complete based on which criteria are met."""
        criteria = self.get_criteria_list()
        required_criteria = [c for c in criteria if c.get("required", True)]

        if not required_criteria:
            return len(met_ids) > 0

        if self.criteria_match_mode == CriteriaMatchMode.ALL:
            return all(c["id"] in met_ids for c in required_criteria)
        elif self.criteria_match_mode == CriteriaMatchMode.ANY:
            return any(c["id"] in met_ids for c in required_criteria)
        elif self.criteria_match_mode == CriteriaMatchMode.MAJORITY:
            met_count = sum(1 for c in required_criteria if c["id"] in met_ids)
            return met_count > len(required_criteria) / 2
        elif self.criteria_match_mode == CriteriaMatchMode.THRESHOLD:
            met_count = sum(1 for c in required_criteria if c["id"] in met_ids)
            return met_count >= self.criteria_threshold

        return False
