"""Turn-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class TurnResponse(BaseModel):
    """Schema for turn response."""

    id: str
    session_id: str
    objective_id: str
    turn_number: int
    actor_message: str
    actor_thinking: Optional[str] = None
    subject_response: str
    subject_thinking: Optional[str] = None
    assessor_evaluation: Dict[str, Any]
    criteria_met: bool
    refusal_detected: bool
    actor_strategy: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AssessorEvaluation(BaseModel):
    """Schema for assessor evaluation results."""

    criteria_status: str  # "met", "partially_met", "not_met"
    progress_notes: str
    refusal_detected: bool
    safety_measures: list[str]
    actor_hint: Optional[str] = None  # Only in sneaky mode
