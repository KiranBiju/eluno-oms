"""SLA breach prediction inference."""

from pathlib import Path

import joblib
import pandas as pd

DEFAULT_MODEL_PATH = "data/models/sla_breach_model.joblib"

_model = None


def load_model(model_path: str = DEFAULT_MODEL_PATH):
    """Load trained model (cached)."""
    global _model
    if _model is None:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Model not found at {path}. Run: python scripts/train_model.py"
            )
        _model = joblib.load(path)
    return _model


def get_risk_level(probability: float) -> str:
    if probability >= 0.70:
        return "High"
    if probability >= 0.40:
        return "Medium"
    return "Low"


def predict_breach_probability(
    lens_type: str,
    current_stage: str,
    days_elapsed: int,
    sla_days: int,
    model_path: str = DEFAULT_MODEL_PATH,
) -> float:
    """Predict SLA breach probability for a single order."""
    try:
        model = load_model(model_path)
    except FileNotFoundError:
        # Heuristic fallback if model not trained
        ratio = days_elapsed / sla_days if sla_days else 1.0
        base = min(0.95, ratio * 0.8)
        if current_stage in ("Quality Check Failed", "Reorder Required"):
            base = min(0.95, base + 0.2)
        return round(base, 4)

    row = pd.DataFrame([{
        "lens_type": lens_type,
        "current_stage": current_stage,
        "days_elapsed": days_elapsed,
        "sla_days": sla_days,
    }])
    proba = model.predict_proba(row)[0]
    classifier = model.named_steps["classifier"]
    classes = list(classifier.classes_)
    delay_idx = classes.index(1) if 1 in classes else -1
    return round(float(proba[delay_idx]), 4)


def run_batch_predictions(orders_data: list[dict]) -> list[dict]:
    """Batch predict for multiple orders."""
    results = []
    for o in orders_data:
        prob = predict_breach_probability(
            lens_type=o["lens_type"],
            current_stage=o["current_stage"],
            days_elapsed=o["days_elapsed"],
            sla_days=o["sla_days"],
        )
        results.append({**o, "breach_probability": prob, "risk_level": get_risk_level(prob)})
    return results
