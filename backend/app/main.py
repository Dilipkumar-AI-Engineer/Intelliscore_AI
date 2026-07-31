"""
FastAPI application entrypoint.

For now this only proves the scaffolding works: config loads from .env,
the app boots, and a health check responds. Real routers (auth, essays,
analysis, etc.) get registered here in later modules via app.include_router().
"""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/health")
def health_check():
    """Basic liveness probe: confirms the app booted and config loaded."""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
    }
