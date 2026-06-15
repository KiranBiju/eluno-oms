"""Initialize database tables."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.session import Base, engine
from backend.models import Alert, Inventory, Order, Prediction, StatusHistory  # noqa: F401


def init_db():
    Path("data").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
