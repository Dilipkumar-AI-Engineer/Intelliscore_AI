"""
Inference: turn a trained model + raw essay text into a predicted score,
WITH an explanation of which features drove the prediction.

Concept -- explainability via feature importance: XGBoost tracks how much
each feature contributed to reducing prediction error across all trees
during training (`model.feature_importances_`). This is a GLOBAL
explanation (which features matter most across all essays in general),
not a per-essay explanation (why THIS essay got THIS score). For a true
per-essay explanation ("this essay lost points specifically because of
X, Y, Z"), the standard upgrade is SHAP (SHapley Additive exPlanations)
values -- flagged here as a natural Module 4+ enhancement once the model
is trained on real data, since SHAP adds real computational cost that
isn't worth paying on a synthetic placeholder model.
"""

import pathlib

import joblib

from ml.features.vectorizer import FEATURE_NAMES, vectorize_text

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL_PATH = REPO_ROOT / "ml" / "models" / "xgboost_essay_scorer.pkl"

_model = None  # lazy-loaded singleton -- avoid re-reading the model file on every call


def _get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. "
                "Run `python -m ml.training.train_model` first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_essay_score(raw_text: str, top_n_factors: int = 5) -> dict:
    """
    Predict an overall score (0-100) for the given essay text, plus the
    top contributing features (global importance, see module docstring).
    """
    model = _get_model()
    vector, features = vectorize_text(raw_text)

    predicted_score = float(model.predict([vector])[0])
    predicted_score = round(max(0.0, min(100.0, predicted_score)), 1)

    importances = model.feature_importances_
    ranked = sorted(zip(FEATURE_NAMES, importances), key=lambda pair: pair[1], reverse=True)
    top_factors = [
        {"feature": name, "importance": round(float(score), 4)}
        for name, score in ranked[:top_n_factors]
    ]

    return {
        "predicted_score": predicted_score,
        "top_contributing_factors": top_factors,
        "features": features,  # full Module 1/2 analysis, for the UI to display alongside the score
    }
