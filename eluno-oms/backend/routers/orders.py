"""Orders API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.ml.predictor import get_risk_level
from backend.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    SLAMetrics,
    StatusHistoryResponse,
    StatusUpdate,
)
from backend.services import order_service, prediction_service

router = APIRouter()


def _enrich_order(order, db: Session) -> dict:
    """Add SLA metrics and latest prediction to order response."""
    sla = order_service.compute_sla_metrics(order)
    pred = prediction_service.get_latest_prediction(db, order.id)
    data = {c.name: getattr(order, c.name) for c in order.__table__.columns}
    data["sla_metrics"] = SLAMetrics(**sla)
    if pred:
        data["breach_probability"] = pred.breach_probability
        data["risk_level"] = get_risk_level(pred.breach_probability)
    else:
        data["breach_probability"] = None
        data["risk_level"] = None
    return data


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    return order_service.get_dashboard_stats(db)


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    store_location: str | None = None,
    lens_type: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    orders = order_service.get_all(
        db, skip=skip, limit=limit,
        status=status, store_location=store_location,
        lens_type=lens_type, search=search,
    )
    return [_enrich_order(o, db) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = order_service.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _enrich_order(order, db)


@router.get("/{order_id}/sla", response_model=SLAMetrics)
def get_order_sla(order_id: int, db: Session = Depends(get_db)):
    order = order_service.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return SLAMetrics(**order_service.compute_sla_metrics(order))


@router.get("/{order_id}/history", response_model=list[StatusHistoryResponse])
def get_order_history(order_id: int, db: Session = Depends(get_db)):
    order = order_service.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.get_status_history(db, order_id)


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = order_service.create(db, data)
    return _enrich_order(order, db)


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    order = order_service.update(db, order_id, data)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _enrich_order(order, db)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        order = order_service.update_status(
            db, order_id, data.new_status, data.reason
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _enrich_order(order, db)
