"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import auth, essays, chat
from app.core.config import settings
from app.db.session import Base, engine
from app.models import Essay, PasswordResetToken, User

# Create tables if they don't exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Add CORS middleware to allow requests from the React frontend (usually localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(essays.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    """Basic liveness probe: confirms the app booted and config loaded."""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
    }
# IntelliScore AI Main FastAPI Application (Reload Trigger)
