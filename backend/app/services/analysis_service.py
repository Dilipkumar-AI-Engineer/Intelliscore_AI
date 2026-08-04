"""
Analysis service: connects the backend to Modules 1-3's ml pipeline.

This is the bridge between the web layer and the framework-agnostic
`ml/` package (a boundary we deliberately preserved since Module 0 --
`ml/` never imports from `backend/`, only the reverse).

Path note: `ml/` lives at the REPO ROOT (sibling to `backend/`), not
inside `backend/app/`. Since uvicorn runs with `backend/` as the working
directory, `ml` is not on sys.path by default -- we add the repo root
explicitly here, using the same REPO_ROOT-from-__file__ pattern as
config.py (Module 0) and db/session.py (Module 5), rather than relying
on the working directory.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.models.essay import Essay  # noqa: E402
from ml.inference.predict_score import predict_essay_score  # noqa: E402
from ml.scoring.sub_scores import compute_all_sub_scores  # noqa: E402


class AnalysisError(Exception):
    pass


def analyze_essay(db: Session, essay: Essay) -> dict:
    """
    Run the full NLP + ML pipeline on an essay's text, persist the
    resulting scores on the Essay row, and return the full analysis
    (scores + raw features) for the API response.
    """
    try:
        prediction = predict_essay_score(essay.raw_text)
    except FileNotFoundError as e:
        raise AnalysisError(
            "No trained scoring model found on the server. "
            "Run `python -m ml.training.generate_synthetic_dataset` and "
            "`python -m ml.training.train_model` first (see Module 3)."
        ) from e

    features = prediction["features"]
    sub_scores = compute_all_sub_scores(features, semantic_coherence=None)

    essay.overall_score = prediction["predicted_score"]
    essay.grammar_score = sub_scores["grammar"]["score"]
    essay.vocabulary_score = sub_scores["vocabulary"]["score"]
    essay.coherence_score = sub_scores["coherence"]["score"]
    essay.argument_score = sub_scores["argument"]["score"]
    essay.readability_score = sub_scores["readability"]["score"]

    from datetime import datetime, timezone
    essay.analyzed_at = datetime.now(timezone.utc)

    db.add(essay)
    db.commit()
    db.refresh(essay)

    return {
        "essay_id": essay.id,
        "overall_score": prediction["predicted_score"],
        "sub_scores": sub_scores,
        "features": features,
    }
