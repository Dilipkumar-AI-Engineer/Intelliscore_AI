"""
Shared pytest configuration for backend tests.

Concept -- why this file exists: FastAPI's `app.dependency_overrides` is
GLOBAL, shared by the single `app` object across the whole test session.
If test_auth.py and test_essay_upload.py each independently set their
OWN override_get_db pointing at their OWN separate in-memory engine,
whichever module pytest imports LAST silently wins for every test file --
the other file's tests then query tables that were never created on the
engine its override actually points to, producing confusing
"no such table" errors that have nothing to do with the test's own logic.

Fix: ONE shared test engine and ONE shared override, defined here in
conftest.py (which pytest auto-discovers and applies session-wide), so
every test file uses the same test database consistently.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Fresh tables before every test, dropped after -- full isolation
    between tests, regardless of which file they're in."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
