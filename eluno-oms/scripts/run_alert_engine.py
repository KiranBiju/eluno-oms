"""Run alert engine: predict risks and send alerts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.session import SessionLocal
from backend.services import prediction_service


def main():
    db = SessionLocal()
    try:
        result = prediction_service.run_predictions(db)
        print(
            f"Alert engine complete: "
            f"{result['orders_scored']} scored, "
            f"{result['high_risk_count']} high risk, "
            f"{result['alerts_triggered']} alerts triggered."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
