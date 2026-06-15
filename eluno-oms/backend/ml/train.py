"""Train RandomForest SLA breach classifier."""

import joblib
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = ["lens_type", "current_stage", "days_elapsed", "sla_days"]
TARGET = "delay_flag"
DEFAULT_MODEL_PATH = "data/models/sla_breach_model.joblib"


def train(
    csv_path: str = "data/synthetic_orders.csv",
    model_path: str = DEFAULT_MODEL_PATH,
) -> str:
    """Train model and save to disk. Returns model path."""
    df = pd.read_csv(csv_path)
    X = df[FEATURES]
    y = df[TARGET]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["lens_type", "current_stage"]),
            ("num", "passthrough", ["days_elapsed", "sla_days"]),
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            class_weight="balanced",
        )),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"Test accuracy: {score:.3f}")

    out = Path(model_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out)
    print(f"Model saved -> {out}")
    return str(out)


if __name__ == "__main__":
    train()
