"""Objective-related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.objective import ObjectiveStatus


class ObjectiveCreate(BaseModel):
    """Schema for creating an objective."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    completion_criteria: str = Field(..., min_length=1)
    chain_order: int = Field(default=0, ge=0)


class ObjectiveChainCreate(BaseModel):
    """Schema for creating a chain of objectives."""

    objectives: List[ObjectiveCreate] = Field(..., min_length=1)


class ObjectiveResponse(BaseModel):
    """Schema for objective response."""

    id: str
    session_id: str
    chain_order: int
    title: str
    description: str
    completion_criteria: str
    status: ObjectiveStatus
    bottleneck_notes: Optional[str] = None
    turns_taken: int
    refusal_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
