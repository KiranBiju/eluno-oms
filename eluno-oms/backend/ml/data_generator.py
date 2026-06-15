"""Generate synthetic historical eyewear order data for ML training."""

import random
from pathlib import Path

import pandas as pd

from backend.utils.workflow import LENS_TYPE_SLA, OrderStatus

STAGES = [
    OrderStatus.ORDER_PLACED,
    OrderStatus.PRESCRIPTION_VERIFIED,
    OrderStatus.LENS_ALLOCATED,
    OrderStatus.MANUFACTURING,
    OrderStatus.QUALITY_CHECK,
    OrderStatus.QUALITY_CHECK_FAILED,
    OrderStatus.REORDER_REQUIRED,
    OrderStatus.DISPATCHED,
]

LENS_TYPES = list(LENS_TYPE_SLA.keys())


def generate_synthetic_data(n_records: int = 1200, output_path: str = "data/synthetic_orders.csv") -> str:
    """Generate realistic synthetic order history for SLA breach prediction."""
    random.seed(42)
    records = []

    for _ in range(n_records):
        lens_type = random.choice(LENS_TYPES)
        sla_days = LENS_TYPE_SLA[lens_type]
        current_stage = random.choice(STAGES)
        days_elapsed = random.randint(0, max(sla_days + 5, 8))

        # QC failure stages increase delay probability
        qc_penalty = current_stage in (
            OrderStatus.QUALITY_CHECK_FAILED,
            OrderStatus.REORDER_REQUIRED,
        )

        # Realistic delay logic
        delay_flag = 0
        if days_elapsed > sla_days * 0.85:
            delay_flag = 1 if random.random() > 0.15 else 0
        if qc_penalty and random.random() > 0.3:
            delay_flag = 1
        if current_stage == OrderStatus.MANUFACTURING and days_elapsed > sla_days * 0.6:
            delay_flag = 1 if random.random() > 0.4 else delay_flag

        records.append({
            "lens_type": lens_type,
            "current_stage": current_stage,
            "days_elapsed": days_elapsed,
            "sla_days": sla_days,
            "delay_flag": delay_flag,
        })

    df = pd.DataFrame(records)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Generated {len(df)} records -> {path}")
    print(f"Delay rate: {df['delay_flag'].mean():.2%}")
    return str(path)


if __name__ == "__main__":
    generate_synthetic_data()
