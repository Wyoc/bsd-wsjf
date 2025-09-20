from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from app.models import (
    WSJFItem,
    WSJFItemBatch,
    WSJFItemCreate,
    WSJFItemResponse,
    WSJFItemUpdate,
)
from app.services import excel_service, wsjf_service

router = APIRouter(prefix="/api", tags=["WSJF"])


@router.get("/items", response_model=list[WSJFItemResponse])
async def get_items(
    program_increment_id: UUID | None = Query(
        None, description="Filter by Program Increment ID"
    ),
):
    """Retrieve all WSJF items with priority rankings.

    Args:
        program_increment_id (UUID | None, optional): Filter by Program Increment ID.
            Defaults to None (returns all items).

    Returns:
        list[WSJFItemResponse]: List of WSJF items with priority rankings.
    """
    return wsjf_service.get_all_items(program_increment_id=program_increment_id)


@router.post("/items", response_model=WSJFItem, status_code=201)
async def create_item(item: WSJFItemCreate):
    """Create a new WSJF item.

    Args:
        item (WSJFItemCreate): The WSJF item data to create.

    Returns:
        WSJFItem: The created WSJF item with generated ID and timestamp.
    """
    return wsjf_service.create_item(item)


@router.get("/items/{item_id}", response_model=WSJFItem)
async def get_item(item_id: UUID):
    """Get a specific WSJF item by ID.

    Args:
        item_id (UUID): The unique identifier of the WSJF item.

    Returns:
        WSJFItem: The requested WSJF item.

    Raises:
        HTTPException: 404 if item not found.
    """
    item = wsjf_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="WSJF item not found")
    return item


@router.put("/items/{item_id}", response_model=WSJFItem)
async def update_item(item_id: UUID, update_data: WSJFItemUpdate):
    """Update an existing WSJF item.

    Args:
        item_id (UUID): The unique identifier of the WSJF item.
        update_data (WSJFItemUpdate): The data to update the item with.

    Returns:
        WSJFItem: The updated WSJF item.

    Raises:
        HTTPException: 404 if item not found.
    """
    updated_item = wsjf_service.update_item(item_id, update_data)
    if not updated_item:
        raise HTTPException(status_code=404, detail="WSJF item not found")
    return updated_item


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: UUID):
    """Delete a WSJF item.

    Args:
        item_id (UUID): The unique identifier of the WSJF item to delete.

    Raises:
        HTTPException: 404 if item not found.
    """
    if not wsjf_service.delete_item(item_id):
        raise HTTPException(status_code=404, detail="WSJF item not found")
    return Response(status_code=204)


@router.post("/items/batch", response_model=list[WSJFItem], status_code=201)
async def create_batch_items(batch: WSJFItemBatch):
    """Create multiple WSJF items in batch.

    Args:
        batch (WSJFItemBatch): Container with list of WSJF items to create.

    Returns:
        list[WSJFItem]: List of created WSJF items.
    """
    return wsjf_service.create_batch(batch.items)


@router.get("/export/excel")
async def export_excel(
    program_increment_id: UUID | None = Query(
        None, description="Filter by Program Increment ID"
    ),
    download: bool = Query(
        False, description="Force download instead of inline display"
    ),
):
    """Generate and download Excel file with WSJF items.

    Args:
        program_increment_id (UUID | None, optional): Filter by Program Increment ID.
            Defaults to None (exports all items).
        download (bool, optional): Force download instead of inline display.
            Defaults to False.

    Returns:
        StreamingResponse: Excel file as streaming response.

    Raises:
        HTTPException: 404 if no WSJF items found.
    """
    from app.services import pi_service
    
    items = wsjf_service.get_all_items(program_increment_id=program_increment_id)

    if not items:
        raise HTTPException(status_code=404, detail="No WSJF items found")

    # Get PI name for filename
    if program_increment_id:
        pi_obj = pi_service.get_pi(program_increment_id)
        pi_name = pi_obj.name if pi_obj else f"PI_{program_increment_id}"
    else:
        pi_name = "All_Items"

    # Generate Excel file
    excel_data = excel_service.generate_excel(items, pi_name)

    # Prepare response
    filename = f"WSJF_{pi_name}.xlsx"
    headers = {
        "Content-Disposition": f"{'attachment' if download else 'inline'}; filename={filename}"
    }

    return StreamingResponse(
        iter([excel_data.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/sample-data", response_model=list[WSJFItemResponse])
async def generate_sample_data():
    """Generate demo WSJF data for testing.

    Returns:
        list[WSJFItemResponse]: List of sample WSJF items with priority rankings.
    """
    return wsjf_service.get_sample_data()


@router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status and service information.
    """
    return {"status": "healthy", "service": "WSJF API"}


@router.get("/stats")
async def get_stats(program_increment_id: UUID | None = Query(None)):
    """Get statistics about WSJF items.

    Args:
        program_increment_id (UUID | None, optional): Filter by Program Increment ID.
            Defaults to None (includes all items).

    Returns:
        dict: Statistics including total items, average WSJF score,
              status distribution, and team distribution.
    """
    items = wsjf_service.get_all_items(program_increment_id=program_increment_id)

    if not items:
        return {
            "total_items": 0,
            "avg_wsjf_score": 0,
            "status_distribution": {},
            "team_distribution": {},
        }

    # Calculate statistics
    total_items = len(items)
    avg_wsjf_score = sum(item.wsjf_score for item in items) / total_items

    status_distribution = {}
    team_distribution = {}

    for item in items:
        # Status distribution
        status = item.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1

        # Team distribution
        team = item.team or "Unassigned"
        team_distribution[team] = team_distribution.get(team, 0) + 1

    return {
        "total_items": total_items,
        "avg_wsjf_score": round(avg_wsjf_score, 2),
        "status_distribution": status_distribution,
        "team_distribution": team_distribution,
        "program_increment_id": str(program_increment_id) if program_increment_id else None,
    }
