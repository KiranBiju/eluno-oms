"""Train the SLA breach prediction model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ml.data_generator import generate_synthetic_data
from backend.ml.train import train


def main():
    csv_path = generate_synthetic_data()
    train(csv_path)


if __name__ == "__main__":
    main()
