"""Persona-related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.persona import (
    Background,
    CommunicationStyle,
    Motivation,
    PersistenceLevel,
    ResourceLevel,
    SkillLevel,
)


class PersonaCreate(BaseModel):
    """Schema for creating a custom persona."""

    # Required fields
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    skill_level: SkillLevel
    resources: ResourceLevel
    background: Background

    # Enhanced behavioral attributes
    motivation: Optional[Motivation] = Motivation.CURIOSITY
    communication_style: Optional[CommunicationStyle] = CommunicationStyle.DIRECT
    persistence_level: Optional[PersistenceLevel] = PersistenceLevel.MEDIUM

    # Personality sliders (0.0 to 1.0)
    patience: float = Field(default=0.5, ge=0.0, le=1.0)
    aggression: float = Field(default=0.3, ge=0.0, le=1.0)
    creativity: float = Field(default=0.5, ge=0.0, le=1.0)
    deception: float = Field(default=0.3, ge=0.0, le=1.0)

    # Detailed guidance
    behavioral_notes: Optional[str] = None
    example_phrases: Optional[str] = None
    domain_knowledge: Optional[str] = None

    # Custom prompts (advanced)
    custom_prompt_prefix: Optional[str] = None
    custom_prompt_suffix: Optional[str] = None


class PersonaResponse(BaseModel):
    """Schema for persona response."""

    id: str
    name: str
    description: str
    skill_level: SkillLevel
    resources: ResourceLevel
    background: Background

    # Enhanced attributes
    motivation: Optional[Motivation] = None
    communication_style: Optional[CommunicationStyle] = None
    persistence_level: Optional[PersistenceLevel] = None

    # Personality sliders
    patience: float = 0.5
    aggression: float = 0.3
    creativity: float = 0.5
    deception: float = 0.3

    # Detailed guidance
    behavioral_notes: Optional[str] = None
    example_phrases: Optional[str] = None
    domain_knowledge: Optional[str] = None

    # Custom prompts
    custom_prompt_prefix: Optional[str] = None
    custom_prompt_suffix: Optional[str] = None

    is_preset: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PersonaListResponse(BaseModel):
    """Schema for listing personas."""

    personas: List[PersonaResponse]
    total: int
