"""API endpoints for session management."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Objective, Session, Persona
from app.schemas.session import (
    SessionCreate,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)

router = APIRouter()


@router.post("", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new simulation session."""
    # Verify persona exists
    persona_result = await db.execute(
        select(Persona).where(Persona.id == session_data.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Convert tool_config to dict if provided
    tool_config_dict = None
    if session_data.tool_config:
        tool_config_dict = session_data.tool_config.model_dump()

    # Create session
    session = Session(
        name=session_data.name,
        max_turns=session_data.max_turns,
        sneaky_mode=session_data.sneaky_mode,
        actor_model=session_data.actor_model,
        assessor_model=session_data.assessor_model,
        subject_model=session_data.subject_model,
        tool_config=tool_config_dict,
        persona_id=session_data.persona_id,
        config_json={
            "actor_model": session_data.actor_model,
            "assessor_model": session_data.assessor_model,
            "subject_model": session_data.subject_model,
            "max_turns": session_data.max_turns,
            "sneaky_mode": session_data.sneaky_mode,
            "persona_id": session_data.persona_id,
            "tool_config": tool_config_dict,
        },
    )
    db.add(session)
    await db.flush()

    # Create objectives
    for i, obj_data in enumerate(session_data.objectives):
        objective = Objective(
            session_id=session.id,
            chain_order=i,
            title=obj_data.title,
            description=obj_data.description,
            completion_criteria=obj_data.completion_criteria,
        )
        db.add(objective)

    await db.commit()
    await db.refresh(session)

    # Load relationships for response
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.objectives), selectinload(Session.turns))
        .where(Session.id == session.id)
    )
    session = result.scalar_one()

    return session


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all simulation sessions."""
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.objectives))
        .order_by(Session.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()

    # Get total count
    count_result = await db.execute(select(Session))
    total = len(count_result.scalars().all())

    return SessionListResponse(sessions=sessions, total=total)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific session with all details."""
    result = await db.execute(
        select(Session)
        .options(
            selectinload(Session.objectives),
            selectinload(Session.turns),
        )
        .where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a session."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_update.name is not None:
        session.name = session_update.name
    if session_update.status is not None:
        session.status = session_update.status

    await db.commit()
    await db.refresh(session)

    return session


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a session and all its data."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()

    return {"status": "deleted", "id": session_id}
