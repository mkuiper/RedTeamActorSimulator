"""API endpoints for session export and import."""

import json
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Objective, Persona, Session, Turn
from app.services.report import ReportService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{session_id}")
async def export_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export a session as JSON."""
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

    # Get persona details
    persona_result = await db.execute(
        select(Persona).where(Persona.id == session.persona_id)
    )
    persona = persona_result.scalar_one_or_none()

    # Build export data
    export_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "session": {
            "id": session.id,
            "name": session.name,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "config": session.config_json,
            "max_turns": session.max_turns,
            "sneaky_mode": session.sneaky_mode,
            "actor_model": session.actor_model,
            "assessor_model": session.assessor_model,
            "subject_model": session.subject_model,
        },
        "persona": {
            "id": persona.id,
            "name": persona.name,
            "description": persona.description,
            "skill_level": persona.skill_level.value,
            "resources": persona.resources.value,
            "background": persona.background.value,
            "behavioral_notes": persona.behavioral_notes,
            "is_preset": persona.is_preset,
        } if persona else None,
        "objectives": [
            {
                "id": obj.id,
                "chain_order": obj.chain_order,
                "title": obj.title,
                "description": obj.description,
                "completion_criteria": obj.completion_criteria,
                "status": obj.status.value,
                "bottleneck_notes": obj.bottleneck_notes,
                "turns_taken": obj.turns_taken,
                "refusal_count": obj.refusal_count,
            }
            for obj in sorted(session.objectives, key=lambda o: o.chain_order)
        ],
        "turns": [
            {
                "id": turn.id,
                "objective_id": turn.objective_id,
                "turn_number": turn.turn_number,
                "actor_message": turn.actor_message,
                "subject_response": turn.subject_response,
                "subject_thinking": turn.subject_thinking,
                "assessor_evaluation": turn.assessor_evaluation,
                "criteria_met": turn.criteria_met,
                "refusal_detected": turn.refusal_detected,
                "actor_strategy": turn.actor_strategy,
                "created_at": turn.created_at.isoformat(),
            }
            for turn in sorted(session.turns, key=lambda t: t.turn_number)
        ],
        "report": session.final_report_md,
    }

    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=session_{session_id}.json"
        },
    )


@router.post("/import")
async def import_session(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Import a session from JSON."""
    try:
        content = await file.read()
        data = json.loads(content)

        if data.get("version") != "1.0":
            raise HTTPException(status_code=400, detail="Unsupported export version")

        session_data = data["session"]
        persona_data = data.get("persona")
        objectives_data = data.get("objectives", [])
        turns_data = data.get("turns", [])

        # Check if persona needs to be created
        persona_id = session_data.get("config", {}).get("persona_id")
        if persona_data and not persona_data.get("is_preset"):
            # Create custom persona
            persona = Persona(
                name=persona_data["name"],
                description=persona_data["description"],
                skill_level=persona_data["skill_level"],
                resources=persona_data["resources"],
                background=persona_data["background"],
                behavioral_notes=persona_data.get("behavioral_notes"),
                is_preset=False,
            )
            db.add(persona)
            await db.flush()
            persona_id = persona.id

        # Create session with new ID
        session = Session(
            name=f"{session_data['name']} (imported)",
            max_turns=session_data["max_turns"],
            sneaky_mode=session_data["sneaky_mode"],
            actor_model=session_data["actor_model"],
            assessor_model=session_data["assessor_model"],
            subject_model=session_data["subject_model"],
            persona_id=persona_id,
            config_json=session_data.get("config", {}),
            status=session_data["status"],
            final_report_md=data.get("report"),
        )
        db.add(session)
        await db.flush()

        # Create objectives with mapping for old->new IDs
        objective_id_map = {}
        for obj_data in objectives_data:
            objective = Objective(
                session_id=session.id,
                chain_order=obj_data["chain_order"],
                title=obj_data["title"],
                description=obj_data["description"],
                completion_criteria=obj_data["completion_criteria"],
                status=obj_data["status"],
                bottleneck_notes=obj_data.get("bottleneck_notes"),
                turns_taken=obj_data.get("turns_taken", 0),
                refusal_count=obj_data.get("refusal_count", 0),
            )
            db.add(objective)
            await db.flush()
            objective_id_map[obj_data["id"]] = objective.id

        # Create turns
        for turn_data in turns_data:
            turn = Turn(
                session_id=session.id,
                objective_id=objective_id_map.get(turn_data["objective_id"], turn_data["objective_id"]),
                turn_number=turn_data["turn_number"],
                actor_message=turn_data["actor_message"],
                subject_response=turn_data["subject_response"],
                subject_thinking=turn_data.get("subject_thinking"),
                assessor_evaluation=turn_data.get("assessor_evaluation", {}),
                criteria_met=turn_data.get("criteria_met", False),
                refusal_detected=turn_data.get("refusal_detected", False),
                actor_strategy=turn_data.get("actor_strategy"),
            )
            db.add(turn)

        await db.commit()

        return {
            "status": "success",
            "session_id": session.id,
            "message": f"Session imported successfully as '{session.name}'",
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{session_id}/md")
async def get_markdown_report(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the Markdown report for a session."""
    report_service = ReportService(session_id)
    report_md = await report_service.generate_markdown()

    return Response(
        content=report_md,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=report_{session_id}.md"
        },
    )


@router.get("/report/{session_id}/pdf")
async def get_pdf_report(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the PDF report for a session."""
    report_service = ReportService(session_id)

    try:
        pdf_bytes = await report_service.generate_pdf()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{session_id}.pdf"
            },
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )
