"""
Auth endpoint tests.

Uses an isolated in-memory SQLite database (NOT the real data/intelliscore.db
file) via FastAPI's dependency override system -- this means running tests
never touches or pollutes your real development database.

Run with: pytest backend/tests/test_auth.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app

# In-memory SQLite: fast, isolated, destroyed automatically after tests.
# StaticPool is REQUIRED here: by default, SQLAlchemy opens a new
# connection per session, and `sqlite:///:memory:` gives each new
# connection its OWN separate empty database -- tables created in one
# session would be invisible to the next. StaticPool forces every
# session to reuse the same single connection, so they all see the same
# in-memory database.
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Swap the real DB session for the test one, for the duration of tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create fresh tables before each test, drop them after -- full isolation."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)

VALID_USER = {
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User",
    "role": "student",
}


def test_register_success():
    response = client.post("/api/v1/auth/register", json=VALID_USER)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == VALID_USER["email"]
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_rejected():
    client.post("/api/v1/auth/register", json=VALID_USER)
    response = client.post("/api/v1/auth/register", json=VALID_USER)
    assert response.status_code == 400


def test_register_weak_password_rejected():
    weak = {**VALID_USER, "email": "weak@example.com", "password": "short"}
    response = client.post("/api/v1/auth/register", json=weak)
    assert response.status_code == 422  # Pydantic validation error


def test_register_password_without_number_rejected():
    weak = {**VALID_USER, "email": "noletters@example.com", "password": "onlyletters"}
    response = client.post("/api/v1/auth/register", json=weak)
    assert response.status_code == 422


def test_login_success_returns_token():
    client.post("/api/v1/auth/register", json=VALID_USER)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_rejected():
    client.post("/api/v1/auth/register", json=VALID_USER)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_USER["email"], "password": "wrongpassword123"},
    )
    assert response.status_code == 401


def test_login_nonexistent_email_rejected():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert response.status_code == 401


def test_protected_route_without_token_rejected():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_protected_route_with_invalid_token_rejected():
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_protected_route_with_valid_token_succeeds():
    client.post("/api/v1/auth/register", json=VALID_USER)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == VALID_USER["email"]


def test_password_is_actually_hashed_in_db():
    """Defensive test: confirm we never accidentally store plaintext passwords."""
    from app.models.user import User

    client.post("/api/v1/auth/register", json=VALID_USER)
    db = TestSessionLocal()
    try:
        user = db.query(User).filter(User.email == VALID_USER["email"]).first()
        assert user is not None
        assert user.hashed_password != VALID_USER["password"]
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash prefix
    finally:
        db.close()
