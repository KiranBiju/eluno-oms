"""Seed sample lens inventory data."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.session import SessionLocal
from backend.models.inventory import Inventory
from backend.utils.workflow import COATINGS, LENS_INDICES, LENS_TYPES

VENDORS = ["Essilor India", "Zeiss Vision", "Hoya Lens", "Local Optics Supply"]


def seed_inventory():
    db = SessionLocal()
    existing = db.query(Inventory).count()
    if existing > 0:
        print(f"Inventory already has {existing} items. Skipping seed.")
        db.close()
        return

    items = []
    for _ in range(40):
        sphere = round(random.choice([-6.0, -4.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0]), 2)
        cylinder = round(random.choice([0.0, -0.5, -1.0, -1.5, -2.0]), 2)
        axis = random.choice([0, 90, 180]) if cylinder != 0 else 0
        items.append(Inventory(
            sphere=sphere,
            cylinder=cylinder,
            axis=axis,
            lens_type=random.choice(LENS_TYPES),
            lens_index=random.choice(LENS_INDICES),
            coating=random.choice(COATINGS),
            stock_quantity=random.randint(0, 25),
            vendor_name=random.choice(VENDORS),
        ))

    db.add_all(items)
    db.commit()
    print(f"Seeded {len(items)} inventory items.")
    db.close()


if __name__ == "__main__":
    seed_inventory()
