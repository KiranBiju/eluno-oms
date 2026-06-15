"""SLA breach prediction service."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.models.order import Order
from backend.models.prediction import Prediction
from backend.ml.predictor import get_risk_level, predict_breach_probability
from backend.services import alert_service, sla_service


def get_latest_prediction(db: Session, order_id: int) -> Prediction | None:
    return (
        db.query(Prediction)
        .filter(Prediction.order_id == order_id)
        .order_by(Prediction.predicted_at.desc())
        .first()
    )


def get_all_predictions(db: Session, limit: int = 100) -> list[dict]:
    """Return latest prediction per order with order details."""
    orders = (
        db.query(Order)
        .filter(Order.status != "Delivered")
        .all()
    )
    results = []
    for order in orders:
        pred = get_latest_prediction(db, order.id)
        if pred:
            results.append({
                "id": pred.id,
                "order_id": order.id,
                "breach_probability": pred.breach_probability,
                "predicted_at": pred.predicted_at,
                "risk_level": get_risk_level(pred.breach_probability),
                "customer_name": order.customer_name,
                "status": order.status,
                "lens_type": order.lens_type,
            })
    results.sort(key=lambda x: x["breach_probability"], reverse=True)
    return results[:limit]


def run_predictions(db: Session) -> dict:
    """Run ML predictions for all active orders and trigger alerts."""
    active_orders = (
        db.query(Order)
        .filter(Order.status != "Delivered")
        .all()
    )

    alerts_triggered = 0
    high_risk_count = 0

    for order in active_orders:
        sla = sla_service.compute_sla_metrics(order)
        prob = predict_breach_probability(
            lens_type=order.lens_type,
            current_stage=order.status,
            days_elapsed=sla["days_elapsed"],
            sla_days=order.sla_days,
        )

        pred = Prediction(
            order_id=order.id,
            breach_probability=prob,
            predicted_at=datetime.utcnow(),
        )
        db.add(pred)

        if get_risk_level(prob) == "High":
            high_risk_count += 1

        alert = alert_service.evaluate_and_alert(db, order, prob)
        if alert:
            alerts_triggered += 1

    db.commit()
    return {
        "orders_scored": len(active_orders),
        "high_risk_count": high_risk_count,
        "alerts_triggered": alerts_triggered,
    }


def get_high_risk_orders(db: Session, threshold: float = 0.7) -> list[dict]:
    predictions = get_all_predictions(db)
    return [p for p in predictions if p["breach_probability"] >= threshold]
