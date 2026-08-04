"""
API client: the ONLY file in the Streamlit app that makes HTTP requests
to the FastAPI backend. Every page imports functions from here instead
of calling `requests` directly -- same facade principle as
ml/nlp/feature_extractor.py (Module 1) and the parser facade (Module 6).

Why this matters for a Streamlit app specifically: if the backend URL
changes (e.g. deploying to a real server instead of localhost), or if we
add retry logic, timeout handling, or error formatting, there's exactly
ONE place to change it -- not five different pages each with their own
requests.post() calls.
"""

import os

import requests
import streamlit as st

# Reads from an environment variable if set (e.g. for deployment), else
# falls back to local development default. This mirrors the .env pattern
# from the backend (Module 0) -- config should never be hardcoded deep
# inside application logic.
BACKEND_URL = os.environ.get("INTELLISCORE_API_URL", "http://127.0.0.1:8000")

DEFAULT_TIMEOUT_SECONDS = 15


class APIError(Exception):
    """Raised for any failed API call, with a user-facing message."""
    pass


def _handle_response(response: requests.Response) -> dict:
    """
    Shared response handling: raise a clean APIError with the backend's
    actual error message on failure, otherwise return the parsed JSON.
    FastAPI's validation/auth errors come back as {"detail": "..."} --
    we surface that detail directly rather than a generic "request failed."
    """
    if response.ok:
        return response.json()

    try:
        detail = response.json().get("detail", "Unknown error")
    except ValueError:
        detail = response.text or f"HTTP {response.status_code}"
    raise APIError(detail)


def register(email: str, password: str, full_name: str, role: str = "student") -> dict:
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": full_name, "role": role},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError as e:
        raise APIError(
            "Could not reach the backend. Is it running? "
            "(uvicorn app.main:app --reload)"
        ) from e
    return _handle_response(response)


def login(email: str, password: str) -> dict:
    """Returns {'access_token': ..., 'user': {...}} on success."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError as e:
        raise APIError(
            "Could not reach the backend. Is it running? "
            "(uvicorn app.main:app --reload)"
        ) from e
    return _handle_response(response)


def _auth_headers() -> dict:
    """Build the Authorization header from the token stored in session_state."""
    token = st.session_state.get("access_token")
    if not token:
        raise APIError("Not logged in.")
    return {"Authorization": f"Bearer {token}"}


def get_current_user() -> dict:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/auth/me", headers=_auth_headers(), timeout=DEFAULT_TIMEOUT_SECONDS
    )
    return _handle_response(response)


def upload_essay(file_bytes: bytes, filename: str) -> dict:
    files = {"file": (filename, file_bytes)}
    response = requests.post(
        f"{BACKEND_URL}/api/v1/essays/upload",
        files=files,
        headers=_auth_headers(),
        timeout=60,  # OCR uploads can take several seconds, per Module 6
    )
    return _handle_response(response)


def list_essays() -> list[dict]:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/essays/", headers=_auth_headers(), timeout=DEFAULT_TIMEOUT_SECONDS
    )
    return _handle_response(response)


def get_essay(essay_id: int) -> dict:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/essays/{essay_id}",
        headers=_auth_headers(),
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )
    return _handle_response(response)
