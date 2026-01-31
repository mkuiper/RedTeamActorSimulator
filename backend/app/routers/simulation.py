"""API endpoints for simulation control."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Objective, Session, Turn
from app.models.objective import ObjectiveStatus
from app.models.session import SessionStatus
from app.schemas.simulation import (
    ObjectiveProgress,
    SimulationStartRequest,
    SimulationStatus,
    SimulationStepResponse,
)
from app.services.simulation import SimulationService

logger = logging.getLogger(__name__)

router = APIRouter()

# Track active simulations
active_simulations: Dict[str, asyncio.Task] = {}


@router.post("/start")
async def start_simulation(
    request: SimulationStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """Start a simulation for a session."""
    # Check if session exists
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.objectives))
        .where(Session.id == request.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == SessionStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Simulation already running")

    # Update session status
    session.status = SessionStatus.RUNNING
    await db.commit()

    # Create simulation service and start in background
    simulation_service = SimulationService(request.session_id)

    # Create background task
    task = asyncio.create_task(simulation_service.run())
    active_simulations[request.session_id] = task

    return {
        "status": "started",
        "session_id": request.session_id,
        "message": "Simulation started. Use /status endpoint to monitor progress.",
    }


@router.post("/stop")
async def stop_simulation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Stop a running simulation."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Simulation not running")

    # Cancel the task if it exists
    if session_id in active_simulations:
        task = active_simulations[session_id]
        task.cancel()
        del active_simulations[session_id]

    # Update session status
    session.status = SessionStatus.STOPPED
    await db.commit()

    return {
        "status": "stopped",
        "session_id": session_id,
    }


@router.get("/status/{session_id}", response_model=SimulationStatus)
async def get_simulation_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get current status of a simulation."""
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

    # Find current objective
    current_objective = None
    for obj in sorted(session.objectives, key=lambda o: o.chain_order):
        if obj.status in [ObjectiveStatus.PENDING, ObjectiveStatus.IN_PROGRESS]:
            current_objective = obj
            break

    # Get last turn
    last_turn = None
    if session.turns:
        last_turn = max(session.turns, key=lambda t: t.turn_number)

    # Build progress list
    objectives_progress = [
        ObjectiveProgress(
            id=obj.id,
            title=obj.title,
            chain_order=obj.chain_order,
            status=obj.status,
            turns_taken=obj.turns_taken,
            refusal_count=obj.refusal_count,
        )
        for obj in sorted(session.objectives, key=lambda o: o.chain_order)
    ]

    return SimulationStatus(
        session_id=session.id,
        session_status=session.status,
        current_objective_id=current_objective.id if current_objective else None,
        current_objective_title=current_objective.title if current_objective else None,
        current_turn=last_turn.turn_number if last_turn else 0,
        max_turns=session.max_turns,
        objectives_progress=objectives_progress,
        last_actor_message=last_turn.actor_message if last_turn else None,
        last_subject_response=last_turn.subject_response if last_turn else None,
        last_assessment=last_turn.assessor_evaluation if last_turn else None,
        started_at=session.created_at,
        completed_at=session.updated_at if session.status == SessionStatus.COMPLETED else None,
    )


@router.get("/stream/{session_id}")
async def stream_simulation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Stream simulation updates via Server-Sent Events."""

    async def event_generator():
        """Generate SSE events for simulation updates."""
        last_turn_count = 0

        while True:
            # Get current session state
            async with db.begin():
                result = await db.execute(
                    select(Session)
                    .options(selectinload(Session.turns))
                    .where(Session.id == session_id)
                )
                session = result.scalar_one_or_none()

                if not session:
                    yield f"data: {{\"error\": \"Session not found\"}}\n\n"
                    break

                # Check for new turns
                current_turn_count = len(session.turns)
                if current_turn_count > last_turn_count:
                    # Get the new turn
                    new_turns = sorted(session.turns, key=lambda t: t.turn_number)[last_turn_count:]
                    for turn in new_turns:
                        event_data = {
                            "type": "turn",
                            "turn_number": turn.turn_number,
                            "actor_message": turn.actor_message,
                            "subject_response": turn.subject_response,
                            "criteria_met": turn.criteria_met,
                            "assessment": turn.assessor_evaluation,
                        }
                        yield f"data: {event_data}\n\n"
                    last_turn_count = current_turn_count

                # Check if simulation is complete
                if session.status in [SessionStatus.COMPLETED, SessionStatus.STOPPED, SessionStatus.FAILED]:
                    yield f"data: {{\"type\": \"complete\", \"status\": \"{session.status.value}\"}}\n\n"
                    break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/step/{session_id}", response_model=SimulationStepResponse)
async def manual_step(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Execute a single simulation step manually (for debugging)."""
    simulation_service = SimulationService(session_id)

    try:
        result = await simulation_service.execute_single_step()
        return result
    except Exception as e:
        logger.error(f"Manual step error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
