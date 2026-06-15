"""Inventory API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.inventory import (
    AvailabilityRequest,
    AvailabilityResponse,
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
)
from backend.services import inventory_service

router = APIRouter()


@router.get("/", response_model=list[InventoryResponse])
def list_inventory(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return inventory_service.get_all(db, skip=skip, limit=limit)


@router.get("/summary")
def inventory_summary(db: Session = Depends(get_db)):
    return inventory_service.get_inventory_summary(db)


@router.get("/availability", response_model=AvailabilityResponse)
def check_availability(
    sphere: float = Query(...),
    cylinder: float = Query(0.0),
    axis: int = Query(0),
    lens_type: str = Query(...),
    coating: str = Query(...),
    db: Session = Depends(get_db),
):
    return inventory_service.check_availability(
        db, sphere, cylinder, axis, lens_type, coating
    )


@router.post("/availability", response_model=AvailabilityResponse)
def check_availability_post(
    req: AvailabilityRequest,
    db: Session = Depends(get_db),
):
    return inventory_service.check_availability(
        db, req.sphere, req.cylinder, req.axis, req.lens_type, req.coating
    )


@router.get("/{item_id}", response_model=InventoryResponse)
def get_inventory(item_id: int, db: Session = Depends(get_db)):
    item = inventory_service.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.post("/", response_model=InventoryResponse, status_code=201)
def create_inventory(data: InventoryCreate, db: Session = Depends(get_db)):
    return inventory_service.create(db, data)


@router.put("/{item_id}", response_model=InventoryResponse)
def update_inventory(
    item_id: int,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
):
    item = inventory_service.update(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    if not inventory_service.delete(db, item_id):
        raise HTTPException(status_code=404, detail="Inventory item not found")
