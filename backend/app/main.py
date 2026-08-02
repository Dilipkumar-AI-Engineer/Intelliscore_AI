"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI

from app.api.v1.routes import auth
from app.core.config import settings
from app.db.session import Base, engine

# Create tables if they don't exist. Fine for SQLite/dev; a real
# production setup would use Alembic migrations instead of this, since
# create_all() can't handle schema CHANGES to existing tables -- only
# creating new ones. Flagged here as a known simplification for now.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(auth.router)


@app.get("/health")
def health_check():
    """Basic liveness probe: confirms the app booted and config loaded."""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
    }
