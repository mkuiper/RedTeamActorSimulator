"""API endpoints for objective presets."""

from fastapi import APIRouter
from typing import List, Dict, Any

from app.models.persona import DEFAULT_OBJECTIVES

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]])
async def list_objective_presets():
    """List all preset objectives for red team testing."""
    return DEFAULT_OBJECTIVES


@router.get("/categories", response_model=List[str])
async def list_objective_categories():
    """List all unique objective categories."""
    categories = list(set(obj["category"] for obj in DEFAULT_OBJECTIVES))
    return sorted(categories)


@router.get("/by-category/{category}", response_model=List[Dict[str, Any]])
async def get_objectives_by_category(category: str):
    """Get all objectives in a specific category."""
    return [obj for obj in DEFAULT_OBJECTIVES if obj["category"] == category]
