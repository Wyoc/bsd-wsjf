from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.models import (
    ProgramIncrement,
    ProgramIncrementCreate,
    ProgramIncrementResponse,
    ProgramIncrementUpdate,
    ProgramIncrementStats,
)
from app.services import pi_service

router = APIRouter(prefix="/api/pis", tags=["Program Increments"])


@router.get("/", response_model=list[ProgramIncrementResponse])
async def get_all_pis():
    """Retrieve all Program Increments with item counts.

    Returns:
        list[ProgramIncrementResponse]: List of Program Increments with item counts.
    """
    return pi_service.get_all_pis()


@router.post("/", response_model=ProgramIncrement, status_code=201)
async def create_pi(pi: ProgramIncrementCreate):
    """Create a new Program Increment.

    Args:
        pi (ProgramIncrementCreate): The PI data to create.

    Returns:
        ProgramIncrement: The created PI with generated ID and timestamp.
    """
    # Check if PI name already exists
    existing_pi = pi_service.get_pi_by_name(pi.name)
    if existing_pi:
        raise HTTPException(
            status_code=409, 
            detail=f"Program Increment with name '{pi.name}' already exists"
        )
    
    return pi_service.create_pi(pi)


@router.get("/{pi_id}", response_model=ProgramIncrement)
async def get_pi(pi_id: UUID):
    """Get a specific Program Increment by ID.

    Args:
        pi_id (UUID): The unique identifier of the PI.

    Returns:
        ProgramIncrement: The requested PI.

    Raises:
        HTTPException: 404 if PI not found.
    """
    pi = pi_service.get_pi(pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Program Increment not found")
    return pi


@router.get("/name/{pi_name}", response_model=ProgramIncrement)
async def get_pi_by_name(pi_name: str):
    """Get a specific Program Increment by name.

    Args:
        pi_name (str): The name of the PI.

    Returns:
        ProgramIncrement: The requested PI.

    Raises:
        HTTPException: 404 if PI not found.
    """
    pi = pi_service.get_pi_by_name(pi_name)
    if not pi:
        raise HTTPException(status_code=404, detail="Program Increment not found")
    return pi


@router.put("/{pi_id}", response_model=ProgramIncrement)
async def update_pi(pi_id: UUID, update_data: ProgramIncrementUpdate):
    """Update an existing Program Increment.

    Args:
        pi_id (UUID): The unique identifier of the PI.
        update_data (ProgramIncrementUpdate): The data to update the PI with.

    Returns:
        ProgramIncrement: The updated PI.

    Raises:
        HTTPException: 404 if PI not found.
    """
    updated_pi = pi_service.update_pi(pi_id, update_data)
    if not updated_pi:
        raise HTTPException(status_code=404, detail="Program Increment not found")
    return updated_pi


@router.delete("/{pi_id}", status_code=204)
async def delete_pi(pi_id: UUID):
    """Delete a Program Increment and all associated WSJF items.

    Args:
        pi_id (UUID): The unique identifier of the PI to delete.

    Raises:
        HTTPException: 404 if PI not found.
    """
    if not pi_service.delete_pi(pi_id):
        raise HTTPException(status_code=404, detail="Program Increment not found")


@router.get("/{pi_id}/stats", response_model=ProgramIncrementStats)
async def get_pi_stats(pi_id: UUID):
    """Get statistics for a Program Increment.

    Args:
        pi_id (UUID): The unique identifier of the PI.

    Returns:
        ProgramIncrementStats: Statistics about the PI including items count,
                              average WSJF score, status distribution, and team distribution.

    Raises:
        HTTPException: 404 if PI not found.
    """
    stats = pi_service.get_pi_stats(pi_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Program Increment not found")
    return stats