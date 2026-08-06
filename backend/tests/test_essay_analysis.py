"""
Tests for POST /api/v1/essays/{id}/analyze.

REQUIRES a trained model on disk (ml/models/xgboost_essay_scorer.pkl) --
run `python -m ml.training.generate_synthetic_dataset` and
`python -m ml.training.train_model` first, same requirement as
ml/tests/test_scoring_model.py.

Run with: pytest backend/tests/test_essay_analysis.py -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TEST_USER = {
    "email": "analysis_test@example.com",
    "password": "testpass123",
    "full_name": "Analysis Tester",
    "role": "student",
}

ESSAY_TEXT = (
    b"Climate change represents a significant global challenge. "
    b"Furthermore, rising temperatures affect ecosystems worldwide. "
    b"Therefore, coordinated international action is essential."
)


@pytest.fixture
def auth_headers():
    client.post("/api/v1/auth/register", json=TEST_USER)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def uploaded_essay_id(auth_headers):
    files = {"file": ("essay.txt", ESSAY_TEXT, "text/plain")}
    response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)
    return response.json()["id"]


def test_analyze_requires_authentication(uploaded_essay_id):
    response = client.post(f"/api/v1/essays/{uploaded_essay_id}/analyze")
    assert response.status_code == 401


def test_analyze_returns_overall_score_and_sub_scores(auth_headers, uploaded_essay_id):
    response = client.post(
        f"/api/v1/essays/{uploaded_essay_id}/analyze", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()

    assert 0 <= body["overall_score"] <= 100
    expected_dimensions = {"grammar", "vocabulary", "coherence", "argument", "readability"}
    assert expected_dimensions.issubset(body["sub_scores"].keys())
    for dim in expected_dimensions:
        assert 0 <= body["sub_scores"][dim]["score"] <= 100
        assert len(body["sub_scores"][dim]["explanation"]) > 0

    assert "features" in body
    assert "basic_stats" in body["features"]


def test_analyze_persists_score_to_essay(auth_headers, uploaded_essay_id):
    client.post(f"/api/v1/essays/{uploaded_essay_id}/analyze", headers=auth_headers)

    # Confirm the score is now visible on the essay list -- this is what
    # the Dashboard page reads to compute Average Score / Highest Score.
    list_response = client.get("/api/v1/essays/", headers=auth_headers)
    essays = list_response.json()
    analyzed = next(e for e in essays if e["id"] == uploaded_essay_id)
    assert analyzed["overall_score"] is not None
    assert analyzed["analyzed_at"] is not None


def test_analyze_nonexistent_essay_returns_404(auth_headers):
    response = client.post("/api/v1/essays/999999/analyze", headers=auth_headers)
    assert response.status_code == 404


def test_cannot_analyze_another_users_essay(auth_headers, uploaded_essay_id):
    other_user = {**TEST_USER, "email": "other_analyzer@example.com"}
    client.post("/api/v1/auth/register", json=other_user)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": other_user["email"], "password": other_user["password"]},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        f"/api/v1/essays/{uploaded_essay_id}/analyze", headers=other_headers
    )
    assert response.status_code == 404
