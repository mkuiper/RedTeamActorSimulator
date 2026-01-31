"""Simulation-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.objective import ObjectiveStatus
from app.models.session import SessionStatus


class SimulationStartRequest(BaseModel):
    """Request to start a simulation."""

    session_id: str


class ObjectiveProgress(BaseModel):
    """Progress information for a single objective."""

    id: str
    title: str
    chain_order: int
    status: ObjectiveStatus
    turns_taken: int
    refusal_count: int


class SimulationStatus(BaseModel):
    """Current status of a running simulation."""

    session_id: str
    session_status: SessionStatus
    current_objective_id: Optional[str] = None
    current_objective_title: Optional[str] = None
    current_turn: int = 0
    max_turns: int
    objectives_progress: List[ObjectiveProgress] = []
    last_actor_message: Optional[str] = None
    last_subject_response: Optional[str] = None
    last_assessment: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SimulationStepResponse(BaseModel):
    """Response from a single simulation step."""

    turn_number: int
    actor_message: str
    subject_response: str
    subject_thinking: Optional[str] = None
    assessment: Dict[str, Any]
    criteria_met: bool
    objective_completed: bool
    simulation_completed: bool


class SimulationReport(BaseModel):
    """Final simulation report."""

    session_id: str
    session_name: str
    completed_at: datetime
    total_turns: int
    objectives_summary: List[ObjectiveProgress]
    bottlenecks: List[str]
    strategies_used: List[str]
    success_rate: float
    refusal_rate: float
    report_markdown: str
