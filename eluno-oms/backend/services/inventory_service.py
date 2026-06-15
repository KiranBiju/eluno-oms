"""Inventory management service."""

from sqlalchemy.orm import Session

from backend.models.inventory import Inventory
from backend.schemas.inventory import InventoryCreate, InventoryUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Inventory]:
    return db.query(Inventory).offset(skip).limit(limit).all()


def get_by_id(db: Session, item_id: int) -> Inventory | None:
    return db.query(Inventory).filter(Inventory.id == item_id).first()


def create(db: Session, data: InventoryCreate) -> Inventory:
    item = Inventory(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item_id: int, data: InventoryUpdate) -> Inventory | None:
    item = get_by_id(db, item_id)
    if not item:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item_id: int) -> bool:
    item = get_by_id(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def check_availability(
    db: Session,
    sphere: float,
    cylinder: float,
    axis: int,
    lens_type: str,
    coating: str,
) -> dict:
    """Check lens availability by prescription and type."""
    item = (
        db.query(Inventory)
        .filter(
            Inventory.sphere == sphere,
            Inventory.cylinder == cylinder,
            Inventory.axis == axis,
            Inventory.lens_type == lens_type,
            Inventory.coating == coating,
            Inventory.stock_quantity > 0,
        )
        .first()
    )

    if item:
        return {
            "availability": "In House",
            "estimated_tat_days": 1,
            "in_stock": True,
            "stock_quantity": item.stock_quantity,
        }
    return {
        "availability": "Vendor Procurement",
        "estimated_tat_days": 4,
        "in_stock": False,
        "stock_quantity": 0,
    }


def get_inventory_summary(db: Session) -> dict:
    """Summary stats for dashboard."""
    items = db.query(Inventory).all()
    in_stock = sum(1 for i in items if i.stock_quantity > 0)
    low_stock = sum(1 for i in items if 0 < i.stock_quantity <= 5)
    out_of_stock = sum(1 for i in items if i.stock_quantity == 0)
    return {
        "total_skus": len(items),
        "in_stock_skus": in_stock,
        "low_stock_skus": low_stock,
        "out_of_stock_skus": out_of_stock,
    }
