"""
Tests for essay upload endpoints. Reuses the isolated in-memory DB
pattern from test_auth.py, and generates real files (like
test_document_parsers.py) to upload through the actual HTTP layer.

Run with: pytest backend/tests/test_essay_upload.py -v
"""

import io

import pytest
from docx import Document
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TEST_USER = {
    "email": "student@example.com",
    "password": "testpass123",
    "full_name": "Test Student",
    "role": "student",
}


@pytest.fixture
def auth_headers():
    """Register + login a test user, return ready-to-use auth headers."""
    client.post("/api/v1/auth/register", json=TEST_USER)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_docx_bytes(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


def test_upload_requires_authentication():
    files = {"file": ("essay.txt", b"Some essay content here.", "text/plain")}
    response = client.post("/api/v1/essays/upload", files=files)
    assert response.status_code == 401


def test_upload_txt_success(auth_headers):
    content = b"This is a test essay about renewable energy and its benefits."
    files = {"file": ("essay.txt", content, "text/plain")}
    response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "essay"
    assert body["file_type"] == "txt"
    assert body["word_count"] == 11


def test_upload_docx_success(auth_headers):
    content = _make_docx_bytes("A sample essay discussing solar panel adoption trends.")
    files = {
        "file": (
            "my_essay.docx",
            content,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["file_type"] == "docx"


def test_upload_unsupported_type_rejected(auth_headers):
    files = {"file": ("essay.xyz", b"content", "application/octet-stream")}
    response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)
    assert response.status_code == 400


def test_upload_empty_file_rejected(auth_headers):
    files = {"file": ("essay.txt", b"", "text/plain")}
    response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)
    assert response.status_code == 400


def test_list_essays_returns_only_own_essays(auth_headers):
    files = {"file": ("essay1.txt", b"First essay content here.", "text/plain")}
    client.post("/api/v1/essays/upload", files=files, headers=auth_headers)

    response = client.get("/api/v1/essays/", headers=auth_headers)
    assert response.status_code == 200
    essays = response.json()
    assert len(essays) == 1
    assert essays[0]["title"] == "essay1"


def test_get_single_essay_includes_full_text(auth_headers):
    content = b"Full text of this essay for detailed retrieval testing."
    files = {"file": ("essay.txt", content, "text/plain")}
    upload_response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)
    essay_id = upload_response.json()["id"]

    response = client.get(f"/api/v1/essays/{essay_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["raw_text"] == content.decode()


def test_get_nonexistent_essay_returns_404(auth_headers):
    response = client.get("/api/v1/essays/99999", headers=auth_headers)
    assert response.status_code == 404


def test_cannot_access_another_users_essay(auth_headers):
    files = {"file": ("private.txt", b"Private essay content.", "text/plain")}
    upload_response = client.post("/api/v1/essays/upload", files=files, headers=auth_headers)
    essay_id = upload_response.json()["id"]

    # Register and log in as a SECOND user.
    other_user = {**TEST_USER, "email": "other@example.com"}
    client.post("/api/v1/auth/register", json=other_user)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": other_user["email"], "password": other_user["password"]},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/api/v1/essays/{essay_id}", headers=other_headers)
    assert response.status_code == 404  # not 403 -- see essays.py comment
