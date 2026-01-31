"""API endpoints for persona management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Persona
from app.models.persona import DEFAULT_PERSONAS
from app.schemas.persona import PersonaCreate, PersonaListResponse, PersonaResponse

router = APIRouter()


async def ensure_presets_exist(db: AsyncSession):
    """Ensure default persona presets exist in database."""
    for preset_data in DEFAULT_PERSONAS:
        result = await db.execute(
            select(Persona).where(
                Persona.name == preset_data["name"],
                Persona.is_preset == True,
            )
        )
        if not result.scalar_one_or_none():
            persona = Persona(**preset_data)
            db.add(persona)
    await db.commit()


@router.get("", response_model=PersonaListResponse)
async def list_personas(
    include_presets: bool = True,
    include_custom: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all personas (presets and custom)."""
    # Ensure presets exist
    await ensure_presets_exist(db)

    query = select(Persona)

    if not include_presets and not include_custom:
        # Return empty if both disabled
        return PersonaListResponse(personas=[], total=0)
    elif not include_presets:
        query = query.where(Persona.is_preset == False)
    elif not include_custom:
        query = query.where(Persona.is_preset == True)

    result = await db.execute(query.order_by(Persona.is_preset.desc(), Persona.name))
    personas = result.scalars().all()

    return PersonaListResponse(personas=personas, total=len(personas))


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific persona."""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return persona


@router.post("", response_model=PersonaResponse)
async def create_persona(
    persona_data: PersonaCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a custom persona."""
    persona = Persona(
        name=persona_data.name,
        description=persona_data.description,
        skill_level=persona_data.skill_level,
        resources=persona_data.resources,
        background=persona_data.background,
        behavioral_notes=persona_data.behavioral_notes,
        is_preset=False,
    )
    db.add(persona)
    await db.commit()
    await db.refresh(persona)

    return persona


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a custom persona (presets cannot be deleted)."""
    result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = result.scalar_one_or_none()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    if persona.is_preset:
        raise HTTPException(status_code=400, detail="Cannot delete preset personas")

    await db.delete(persona)
    await db.commit()

    return {"status": "deleted", "id": persona_id}
