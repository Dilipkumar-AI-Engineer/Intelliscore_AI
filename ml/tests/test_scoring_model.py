"""
Tests for Module 3: ML scoring model.

Run with: pytest ml/tests/test_scoring_model.py -v

Note: these tests assume a trained model already exists at
ml/models/xgboost_essay_scorer.pkl. Run the pipeline first:
    python -m ml.training.generate_synthetic_dataset
    python -m ml.training.train_model
"""

import pytest

from ml.features.vectorizer import FEATURE_NAMES, vectorize_features, vectorize_text
from ml.inference.predict_score import predict_essay_score
from ml.nlp.feature_extractor import extract_features

SAMPLE_ESSAY = """
Education plays a crucial role in shaping society. Furthermore, access to quality
education determines long-term economic outcomes for individuals and nations alike.

Therefore, governments must prioritize investment in schools and teacher training.
In conclusion, sustained commitment to education policy benefits everyone.
"""


def test_vectorize_features_matches_feature_names_length():
    features = extract_features(SAMPLE_ESSAY)
    vector = vectorize_features(features)
    assert len(vector) == len(FEATURE_NAMES)


def test_vectorize_features_all_numeric():
    features = extract_features(SAMPLE_ESSAY)
    vector = vectorize_features(features)
    assert all(isinstance(v, (int, float)) for v in vector)


def test_vectorize_text_convenience_wrapper():
    vector, features = vectorize_text(SAMPLE_ESSAY)
    assert len(vector) == len(FEATURE_NAMES)
    assert "basic_stats" in features


def test_vectorizer_handles_essay_with_no_named_entities():
    # Edge case: an essay with zero named entities should still produce
    # a full-length vector with 0 in that slot, not crash or omit it.
    plain_essay = "This is a simple sentence. It has no proper nouns at all."
    vector, _ = vectorize_text(plain_essay)
    assert len(vector) == len(FEATURE_NAMES)
    entity_count_index = FEATURE_NAMES.index("named_entity_count")
    assert vector[entity_count_index] == 0


def test_predict_essay_score_returns_valid_range():
    result = predict_essay_score(SAMPLE_ESSAY)
    assert 0 <= result["predicted_score"] <= 100


def test_predict_essay_score_includes_explanation():
    result = predict_essay_score(SAMPLE_ESSAY)
    assert len(result["top_contributing_factors"]) == 5
    for factor in result["top_contributing_factors"]:
        assert "feature" in factor
        assert "importance" in factor
        assert factor["feature"] in FEATURE_NAMES


def test_predict_essay_score_includes_full_features():
    result = predict_essay_score(SAMPLE_ESSAY)
    assert "features" in result
    assert "basic_stats" in result["features"]


def test_missing_model_raises_clear_error(tmp_path, monkeypatch):
    import ml.inference.predict_score as predict_module

    # Point the module at a path that doesn't exist and reset the cached
    # singleton, to verify the error message is clear rather than a raw
    # FileNotFoundError from joblib.
    monkeypatch.setattr(predict_module, "MODEL_PATH", tmp_path / "nonexistent.pkl")
    monkeypatch.setattr(predict_module, "_model", None)

    with pytest.raises(FileNotFoundError, match="No trained model found"):
        predict_module.predict_essay_score(SAMPLE_ESSAY)
