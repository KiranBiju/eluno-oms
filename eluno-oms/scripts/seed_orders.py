"""Seed sample orders for demo."""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.session import SessionLocal
from backend.models.order import Order
from backend.models.status_history import StatusHistory
from backend.utils.workflow import COATINGS, LENS_INDICES, LENS_TYPES, OrderStatus, STORE_LOCATIONS, default_sla_days

CUSTOMERS = [
    ("Rahul Sharma", "9876543210"),
    ("Priya Menon", "9123456780"),
    ("Arjun Patel", "9988776655"),
    ("Sneha Reddy", "9012345678"),
    ("Vikram Singh", "8765432109"),
    ("Ananya Iyer", "9654321098"),
    ("Karthik Nair", "9543210987"),
    ("Divya Gupta", "9432109876"),
]

FRAMES = ["Eluno Classic", "Eluno Air", "Eluno Bold", "Eluno Sport", "Eluno Premium"]
STATUSES = [
    OrderStatus.ORDER_PLACED,
    OrderStatus.PRESCRIPTION_VERIFIED,
    OrderStatus.LENS_ALLOCATED,
    OrderStatus.MANUFACTURING,
    OrderStatus.QUALITY_CHECK,
    OrderStatus.QUALITY_CHECK_FAILED,
    OrderStatus.DISPATCHED,
]


def seed_orders():
    db = SessionLocal()
    existing = db.query(Order).count()
    if existing > 0:
        print(f"Orders already has {existing} records. Skipping seed.")
        db.close()
        return

    for i, (name, phone) in enumerate(CUSTOMERS):
        lens_type = LENS_TYPES[i % len(LENS_TYPES)]
        sla = default_sla_days(lens_type) + random.choice([1, 4])
        days_ago = random.randint(1, 8)
        status = STATUSES[i % len(STATUSES)]

        order = Order(
            customer_name=name,
            customer_phone=phone,
            store_location=STORE_LOCATIONS[i % len(STORE_LOCATIONS)],
            sphere=round(random.choice([-4.0, -2.0, 0.0, 2.0, 3.0]), 2),
            cylinder=round(random.choice([0.0, -0.5, -1.0]), 2),
            axis=random.choice([0, 90, 180]),
            lens_type=lens_type,
            lens_index=random.choice(LENS_INDICES),
            coating=random.choice(COATINGS),
            frame_name=FRAMES[i % len(FRAMES)],
            status=status,
            sla_days=sla,
            expected_delivery=datetime.utcnow() + timedelta(days=max(0, sla - days_ago)),
            created_at=datetime.utcnow() - timedelta(days=days_ago),
        )
        db.add(order)
        db.flush()

        db.add(StatusHistory(
            order_id=order.id,
            old_status="",
            new_status=OrderStatus.ORDER_PLACED,
            reason="Order created",
        ))
        if status != OrderStatus.ORDER_PLACED:
            db.add(StatusHistory(
                order_id=order.id,
                old_status=OrderStatus.ORDER_PLACED,
                new_status=status,
                reason="Demo seed progression",
            ))

    db.commit()
    print(f"Seeded {len(CUSTOMERS)} sample orders.")
    db.close()


if __name__ == "__main__":
    seed_orders()
