"""
Database engine and session management.

Concept: SQLAlchemy's `sessionmaker` creates a factory for database
sessions -- each incoming API request gets its OWN session (via the
`get_db` dependency below), used for that request only, then closed.
This isolation matters: sharing one session across concurrent requests
would cause data from one user's request to leak into another's queries.

`check_same_thread=False` is SQLite-specific: SQLite normally restricts
a connection to the thread that created it, but FastAPI can serve
requests from different threads. This is safe here because each request
gets its own session/connection via the dependency below -- we're not
sharing a single connection across threads simultaneously.
"""

import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Resolve a relative sqlite:///./data/... URL into an ABSOLUTE path
# rooted at the repo root -- same reasoning as config.py's ENV_FILE_PATH
# fix in Module 0: relying on the process's current working directory
# breaks the moment uvicorn/pytest/Docker launches from a different
# directory. We also ensure the parent folder exists, since SQLite
# will not create missing directories on its own.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

database_url = settings.database_url
if database_url.startswith("sqlite:///./"):
    relative_path = database_url.replace("sqlite:///./", "")
    absolute_path = REPO_ROOT / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite:///{absolute_path}"

connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""
    pass


def get_db():
    """
    FastAPI dependency: yields a database session for a single request,
    guaranteed to close afterward (even if the request raises an error).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
