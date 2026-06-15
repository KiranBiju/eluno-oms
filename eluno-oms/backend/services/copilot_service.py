"""AI Operations Copilot service using Groq Llama."""

from collections import Counter

from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.order import Order
from backend.models.inventory import Inventory
from backend.services import order_service, prediction_service, sla_service


def build_ops_context(db: Session) -> tuple[str, dict]:
    """Build structured operational context from database."""
    orders = db.query(Order).all()
    active = [o for o in orders if o.status != "Delivered"]

    breached = []
    at_risk = []
    delay_by_lens: Counter = Counter()

    for order in active:
        sla = sla_service.compute_sla_metrics(order)
        if sla["sla_health"] == "Red":
            breached.append({
                "id": order.id,
                "customer": order.customer_name,
                "status": order.status,
                "days_elapsed": sla["days_elapsed"],
                "sla_days": order.sla_days,
                "delay_reason": sla["delay_reason"],
            })
        if sla["sla_health"] in ("Red", "Yellow"):
            at_risk.append(order.id)
        if sla["delay_reason"]:
            delay_by_lens[order.lens_type] += 1

    high_risk = prediction_service.get_high_risk_orders(db)

    low_stock = (
        db.query(Inventory)
        .filter(Inventory.stock_quantity <= 5)
        .order_by(Inventory.stock_quantity.asc())
        .limit(10)
        .all()
    )

    status_counts = Counter(o.status for o in active)

    snapshot = {
        "total_orders": len(orders),
        "active_orders": len(active),
        "breached_count": len(breached),
        "high_risk_orders": high_risk[:10],
        "breached_orders": breached[:10],
        "delay_by_lens_type": dict(delay_by_lens),
        "status_breakdown": dict(status_counts),
        "low_stock_items": [
            {
                "sphere": i.sphere,
                "cylinder": i.cylinder,
                "lens_type": i.lens_type,
                "coating": i.coating,
                "stock": i.stock_quantity,
            }
            for i in low_stock
        ],
    }

    context_text = f"""
ELUNO OMS OPERATIONAL SNAPSHOT
==============================
Total Orders: {snapshot['total_orders']}
Active Orders: {snapshot['active_orders']}
Breached/At-Risk Orders: {snapshot['breached_count']}

STATUS BREAKDOWN (Active):
{chr(10).join(f"  - {k}: {v}" for k, v in status_counts.items())}

HIGH RISK ORDERS (breach probability > 70%):
{chr(10).join(f"  - Order #{p['order_id']}: {p['customer_name']}, {p['status']}, {p['breach_probability']*100:.1f}% risk" for p in high_risk[:5]) or "  None"}

BREACHED SLAs:
{chr(10).join(f"  - Order #{b['id']}: {b['customer']}, {b['status']}, elapsed {b['days_elapsed']}/{b['sla_days']} days, reason: {b['delay_reason']}" for b in breached[:5]) or "  None"}

DELAYS BY LENS TYPE:
{chr(10).join(f"  - {k}: {v} delayed orders" for k, v in delay_by_lens.items()) or "  None"}

LOW STOCK INVENTORY (restock candidates):
{chr(10).join(f"  - SPH {i.sphere} CYL {i.cylinder} {i.lens_type} {i.coating}: {i.stock_quantity} units" for i in low_stock[:5]) or "  None"}
""".strip()

    return context_text, snapshot


def answer_question(db: Session, question: str) -> dict:
    """Answer operational question using Groq LLM with DB context."""
    context_text, snapshot = build_ops_context(db)

    if not settings.groq_api_key:
        return _fallback_answer(db, question, snapshot)

    try:
        from groq import Groq

        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Eluno's internal eyewear operations copilot. "
                        "Answer ONLY using the provided operational data. "
                        "Be concise, actionable, and cite specific order IDs when relevant. "
                        "If data is insufficient, say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Operational Data:\n{context_text}\n\nQuestion: {question}",
                },
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content or "No response generated."
    except Exception as exc:
        answer = f"Groq API unavailable ({exc}). Using rule-based fallback.\n\n"
        answer += _fallback_answer(db, question, snapshot)["answer"]

    return {"answer": answer, "context_snapshot": snapshot}


def _fallback_answer(db: Session, question: str, snapshot: dict) -> dict:
    """Rule-based fallback when Groq is not configured."""
    q = question.lower()

    if "highest risk" in q or "high risk" in q:
        risks = snapshot.get("high_risk_orders", [])
        if not risks:
            return {"answer": "No high-risk orders currently.", "context_snapshot": snapshot}
        lines = [
            f"Order #{r['order_id']}: {r['customer_name']} — {r['breach_probability']*100:.1f}% breach risk ({r['status']})"
            for r in risks[:5]
        ]
        return {"answer": "Highest risk orders:\n" + "\n".join(lines), "context_snapshot": snapshot}

    if "breach" in q:
        breached = snapshot.get("breached_orders", [])
        if not breached:
            return {"answer": "No breached orders currently.", "context_snapshot": snapshot}
        lines = [
            f"Order #{b['id']}: {b['customer']} — {b['delay_reason']}"
            for b in breached
        ]
        return {"answer": "Breached orders:\n" + "\n".join(lines), "context_snapshot": snapshot}

    if "delay" in q and "lens" in q:
        delays = snapshot.get("delay_by_lens_type", {})
        if not delays:
            return {"answer": "No significant delays by lens type.", "context_snapshot": snapshot}
        sorted_delays = sorted(delays.items(), key=lambda x: x[1], reverse=True)
        lines = [f"{k}: {v} delayed orders" for k, v in sorted_delays]
        return {"answer": "Lens types causing most delays:\n" + "\n".join(lines), "context_snapshot": snapshot}

    if "restock" in q or "inventory" in q:
        items = snapshot.get("low_stock_items", [])
        if not items:
            return {"answer": "All inventory levels are adequate.", "context_snapshot": snapshot}
        lines = [
            f"SPH {i['sphere']} CYL {i['cylinder']} {i['lens_type']} {i['coating']}: {i['stock']} units"
            for i in items
        ]
        return {"answer": "Restock recommendations:\n" + "\n".join(lines), "context_snapshot": snapshot}

    if "bottleneck" in q:
        breakdown = snapshot.get("status_breakdown", {})
        if breakdown:
            top = max(breakdown.items(), key=lambda x: x[1])
            return {
                "answer": f"Primary bottleneck: '{top[0]}' with {top[1]} orders. "
                f"Active orders: {snapshot['active_orders']}, breached: {snapshot['breached_count']}.",
                "context_snapshot": snapshot,
            }

    # Order-specific query
    import re
    match = re.search(r"order\s*#?\s*(\d+)", q)
    if match:
        order_id = int(match.group(1))
        order = order_service.get_by_id(db, order_id)
        if order:
            sla = sla_service.compute_sla_metrics(order)
            history = order_service.get_status_history(db, order_id)
            hist_lines = [f"  {h.old_status} → {h.new_status} ({h.reason or 'N/A'})" for h in history]
            return {
                "answer": (
                    f"Order #{order_id} — {order.customer_name}\n"
                    f"Status: {order.status}\n"
                    f"Lens: {order.lens_type} ({order.lens_index}, {order.coating})\n"
                    f"SLA: {sla['days_elapsed']}/{sla['sla_days']} days elapsed, health: {sla['sla_health']}\n"
                    f"Delay reason: {sla['delay_reason'] or 'None'}\n"
                    f"History:\n" + "\n".join(hist_lines)
                ),
                "context_snapshot": snapshot,
            }
        return {"answer": f"Order #{order_id} not found.", "context_snapshot": snapshot}

    return {
        "answer": (
            f"Active orders: {snapshot['active_orders']}, "
            f"breached: {snapshot['breached_count']}. "
            "Ask about specific orders, high-risk orders, delays by lens type, "
            "inventory restocking, or operational bottlenecks."
        ),
        "context_snapshot": snapshot,
    }
