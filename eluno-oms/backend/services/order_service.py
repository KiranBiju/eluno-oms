"""Order management service."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.models.order import Order
from backend.models.status_history import StatusHistory
from backend.schemas.order import OrderCreate, OrderUpdate
from backend.services import inventory_service, sla_service
from backend.utils.workflow import (
    OrderStatus,
    can_transition,
    default_sla_days,
    get_valid_next_statuses,
)


def get_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    store_location: str | None = None,
    lens_type: str | None = None,
    search: str | None = None,
) -> list[Order]:
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if store_location:
        query = query.filter(Order.store_location == store_location)
    if lens_type:
        query = query.filter(Order.lens_type == lens_type)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (Order.customer_name.ilike(term))
            | (Order.customer_phone.ilike(term))
            | (Order.frame_name.ilike(term))
        )
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_by_id(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def create(db: Session, data: OrderCreate) -> Order:
    sla_days = default_sla_days(data.lens_type)
    availability = inventory_service.check_availability(
        db,
        data.sphere,
        data.cylinder,
        data.axis,
        data.lens_type,
        data.coating,
    )
    total_tat = sla_days + availability["estimated_tat_days"]
    expected_delivery = datetime.utcnow() + timedelta(days=total_tat)

    order = Order(
        **data.model_dump(),
        status=OrderStatus.ORDER_PLACED,
        sla_days=total_tat,
        expected_delivery=expected_delivery,
    )
    db.add(order)
    db.flush()

    history = StatusHistory(
        order_id=order.id,
        old_status="",
        new_status=OrderStatus.ORDER_PLACED,
        reason="Order created",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return order


def update(db: Session, order_id: int, data: OrderUpdate) -> Order | None:
    order = get_by_id(db, order_id)
    if not order:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(order, key, value)
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


def update_status(
    db: Session,
    order_id: int,
    new_status: str,
    reason: str | None = None,
) -> Order | None:
    order = get_by_id(db, order_id)
    if not order:
        return None

    if not can_transition(order.status, new_status):
        raise ValueError(
            f"Invalid transition from '{order.status}' to '{new_status}'. "
            f"Valid: {get_valid_next_statuses(order.status)}"
        )

    old_status = order.status
    order.status = new_status
    order.updated_at = datetime.utcnow()

    history = StatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return order


def get_status_history(db: Session, order_id: int) -> list[StatusHistory]:
    return (
        db.query(StatusHistory)
        .filter(StatusHistory.order_id == order_id)
        .order_by(StatusHistory.changed_at.asc())
        .all()
    )


def get_dashboard_stats(db: Session) -> dict:
    orders = db.query(Order).all()
    active_statuses = {
        OrderStatus.ORDER_PLACED,
        OrderStatus.PRESCRIPTION_VERIFIED,
        OrderStatus.LENS_ALLOCATED,
        OrderStatus.MANUFACTURING,
        OrderStatus.QUALITY_CHECK,
        OrderStatus.QUALITY_CHECK_FAILED,
        OrderStatus.REORDER_REQUIRED,
        OrderStatus.DISPATCHED,
    }
    active = [o for o in orders if o.status in active_statuses]
    delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
    breached = [
        o for o in active if compute_sla_metrics(o)["sla_health"] == "Red"
    ]
    return {
        "total_orders": len(orders),
        "active_orders": len(active),
        "delivered_orders": len(delivered),
        "breached_or_at_risk": len(breached),
    }


def compute_sla_metrics(order: Order) -> dict:
    return sla_service.compute_sla_metrics(order)
