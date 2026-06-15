"""Alerts API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.order import Order
from backend.schemas.alert import AlertResponse
from backend.services import alert_service

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
def list_alerts(limit: int = 100, db: Session = Depends(get_db)):
    alerts = alert_service.get_all(db, limit=limit)
    results = []
    for alert in alerts:
        order = db.query(Order).filter(Order.id == alert.order_id).first()
        results.append({
            "id": alert.id,
            "order_id": alert.order_id,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "created_at": alert.created_at,
            "customer_name": order.customer_name if order else None,
            "order_status": order.status if order else None,
        })
    return results
