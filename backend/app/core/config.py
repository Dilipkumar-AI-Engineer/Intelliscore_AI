"""
Centralized application settings.

Why this pattern:
- Every setting is declared ONCE here with a type and (optionally) a default.
- pydantic-settings reads values from environment variables / the .env file
  and VALIDATES them at startup — so a missing or malformed value fails
  loudly and immediately, not silently three modules later.
- Every other module imports `settings` from here instead of calling
  os.environ.get(...) directly. That means there is exactly one place to
  look when you need to know "what config does this app have?"
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py is at backend/app/core/config.py -> repo root is 3 levels up.
# We resolve this as an ABSOLUTE path so `.env` loads correctly no matter
# which directory you run `uvicorn` or `pytest` from. Relying on the
# current working directory is a classic source of "works on my machine"
# bugs — e.g. it works when run from repo root but breaks in Docker or CI.
REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE_PATH = REPO_ROOT / ".env"


class Settings(BaseSettings):
    # ---------- App ----------
    app_name: str = "IntelliScore AI"
    environment: str = "development"
    debug: bool = True

    # ---------- Security ----------
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ---------- Database ----------
    database_url: str = "sqlite:///./data/intelliscore.db"

    # ---------- LLM Provider ----------
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # ---------- File Uploads ----------
    max_upload_size_mb: int = 20
    upload_dir: str = "./data/uploads"

    # ---------- Vector Store ----------
    faiss_index_dir: str = "./vectorstore"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# A single, importable instance — created once, reused everywhere.
# e.g. `from app.core.config import settings; settings.database_url`
settings = Settings()
