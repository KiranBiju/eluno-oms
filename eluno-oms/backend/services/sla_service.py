"""SLA calculation engine."""

from datetime import datetime

from backend.models.order import Order


def compute_sla_metrics(order: Order) -> dict:
    """Compute SLA metrics for an order."""
    now = datetime.utcnow()
    elapsed = max(0, (now - order.created_at).days)
    remaining = order.sla_days - elapsed
    pct_used = elapsed / order.sla_days if order.sla_days else 1.0

    if order.status == "Delivered":
        health = "Green"
    elif remaining <= 0:
        health = "Red"
    elif pct_used >= 0.75:
        health = "Red"
    elif pct_used >= 0.50:
        health = "Yellow"
    else:
        health = "Green"

    delay_reason = None
    if remaining < 0:
        delay_reason = f"SLA breached by {abs(remaining)} day(s)"
    elif order.status in ("Quality Check Failed", "Reorder Required"):
        delay_reason = "QC failure / reorder in progress"
    elif order.status == "Manufacturing" and pct_used >= 0.6:
        delay_reason = "Extended time in manufacturing"

    return {
        "sla_days": order.sla_days,
        "days_elapsed": elapsed,
        "time_remaining_days": remaining,
        "sla_health": health,
        "expected_delivery": order.expected_delivery,
        "delay_reason": delay_reason,
    }
