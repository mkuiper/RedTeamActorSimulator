"""API endpoints for preset objectives management."""

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.models.persona import DEFAULT_OBJECTIVES

router = APIRouter()


class ObjectivePreset(BaseModel):
    """Schema for preset objective."""

    category: str
    title: str
    description: str
    completion_criteria: str
    difficulty: str
    chain_position: Optional[int] = None
    chain_total: Optional[int] = None


class ObjectivePresetListResponse(BaseModel):
    """Response for listing preset objectives."""

    objectives: List[ObjectivePreset]
    categories: List[str]
    total: int


@router.get("/presets", response_model=ObjectivePresetListResponse)
async def list_objective_presets(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (easy, medium, hard)"),
):
    """List all preset objective scenarios for AI safety testing."""
    objectives = DEFAULT_OBJECTIVES

    # Filter by category if specified
    if category:
        objectives = [o for o in objectives if o["category"].lower() == category.lower()]

    # Filter by difficulty if specified
    if difficulty:
        objectives = [o for o in objectives if o["difficulty"].lower() == difficulty.lower()]

    # Get unique categories
    all_categories = sorted(set(o["category"] for o in DEFAULT_OBJECTIVES))

    return ObjectivePresetListResponse(
        objectives=[ObjectivePreset(**o) for o in objectives],
        categories=all_categories,
        total=len(objectives),
    )


@router.get("/presets/categories")
async def list_objective_categories():
    """List all objective categories."""
    categories = {}
    for obj in DEFAULT_OBJECTIVES:
        cat = obj["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "difficulties": set()}
        categories[cat]["count"] += 1
        categories[cat]["difficulties"].add(obj["difficulty"])

    return {
        "categories": [
            {
                "name": name,
                "count": data["count"],
                "difficulties": sorted(data["difficulties"]),
            }
            for name, data in sorted(categories.items())
        ]
    }


@router.get("/presets/chains")
async def list_objective_chains():
    """List multi-step attack chains."""
    chains = {}
    for obj in DEFAULT_OBJECTIVES:
        if obj.get("chain_position"):
            # Extract chain ID from title or create one
            chain_key = f"{obj['category']}"
            if chain_key not in chains:
                chains[chain_key] = {
                    "category": obj["category"],
                    "total_steps": obj.get("chain_total", 1),
                    "steps": [],
                }
            chains[chain_key]["steps"].append({
                "position": obj["chain_position"],
                "title": obj["title"],
                "description": obj["description"],
                "completion_criteria": obj["completion_criteria"],
                "difficulty": obj["difficulty"],
            })

    # Sort steps within each chain
    for chain in chains.values():
        chain["steps"].sort(key=lambda x: x["position"])

    return {"chains": list(chains.values())}
