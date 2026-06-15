"""Automated alert service."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.alert import Alert
from backend.utils.email import send_alert_email


def get_all(db: Session, limit: int = 100) -> list[Alert]:
    return (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_alert(db: Session, order_id: int, hours: int = 24) -> Alert | None:
    """Check if an alert was already sent for this order recently."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(Alert)
        .filter(
            Alert.order_id == order_id,
            Alert.alert_type == "SLA_BREACH",
            Alert.created_at >= cutoff,
        )
        .first()
    )


def evaluate_and_alert(db: Session, order, breach_probability: float) -> Alert | None:
    """Create alert and send email if breach probability exceeds threshold."""
    if breach_probability <= settings.breach_alert_threshold:
        return None

    if get_recent_alert(db, order.id):
        return None

    message = (
        f"Order #{order.id} ({order.customer_name}) at '{order.status}' "
        f"has {breach_probability * 100:.1f}% breach risk. "
        f"Recommended: escalate to lab lead and confirm lens procurement."
    )

    alert = Alert(
        order_id=order.id,
        alert_type="SLA_BREACH",
        message=message,
    )
    db.add(alert)
    db.flush()

    send_alert_email(
        subject=f"[Eluno OMS] High Risk Order #{order.id}",
        body=f"""Order ID: {order.id}
Customer: {order.customer_name}
Current Status: {order.status}
Risk Percentage: {breach_probability * 100:.1f}%
Recommended Action: Escalate manufacturing queue and verify inventory/vendor ETA.
""".strip(),
    )
    return alert
