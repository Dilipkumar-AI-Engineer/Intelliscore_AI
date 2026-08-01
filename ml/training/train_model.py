"""
Model training script.

Concept: we split data into train/test sets so we can measure how well
the model generalizes to essays it hasn't seen -- a model that just
memorizes its training data (overfitting) would show great training
performance but be useless in production. We report three standard
regression metrics:

  - MAE  (Mean Absolute Error): average size of the prediction error, in
    the same units as the score (e.g. "predictions are off by ~5 points
    on average"). Easiest metric to explain to a non-technical audience.
  - RMSE (Root Mean Squared Error): like MAE but penalizes large errors
    more heavily (squaring), useful for catching a model that's mostly
    accurate but occasionally wildly wrong.
  - R^2  (Coefficient of Determination): proportion of score variance the
    model explains, 0-1 scale (1 = perfect). Standard "how good is this
    model overall" summary number.

Usage:
    python -m ml.training.train_model
"""

import json
import pathlib

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ml.features.vectorizer import FEATURE_NAMES

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = REPO_ROOT / "data" / "processed" / "synthetic_training_data.csv"
MODEL_OUTPUT_PATH = REPO_ROOT / "ml" / "models" / "xgboost_essay_scorer.pkl"
METRICS_OUTPUT_PATH = REPO_ROOT / "ml" / "models" / "training_metrics.json"


def train_model(data_path: pathlib.Path = DEFAULT_DATA_PATH) -> dict:
    """Train, evaluate, and persist the XGBoost essay scoring model."""
    df = pd.read_csv(data_path)

    missing_columns = set(FEATURE_NAMES + ["score"]) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    X = df[FEATURE_NAMES]
    y = df["score"]

    # 80/20 train/test split. random_state fixes the split so results are
    # reproducible across runs -- essential for debugging and for fair
    # comparison when you later swap in the real ASAP-AES dataset.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        objective="reg:squarederror",
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    metrics = {
        "mae": round(float(mean_absolute_error(y_test, predictions)), 3),
        "rmse": round(float(mean_squared_error(y_test, predictions) ** 0.5), 3),
        "r2": round(float(r2_score(y_test, predictions)), 3),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)

    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    metrics = train_model()
    print("Training complete.")
    print(json.dumps(metrics, indent=2))
    print(f"\nModel saved to: {MODEL_OUTPUT_PATH}")
