"""
Essay service: business logic for uploading and storing essays.
"""

import pathlib
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.essay import Essay
from app.utils.parsers.document_parser import extract_text

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


class EssayUploadError(Exception):
    pass


def save_uploaded_file(file_bytes: bytes, original_filename: str) -> str:
    """
    Save an uploaded file to disk with a UUID-prefixed name to avoid
    collisions (two students uploading files both named "essay.pdf").
    Returns the ABSOLUTE path to the saved file.
    """
    upload_dir = REPO_ROOT / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = pathlib.Path(original_filename).suffix
    safe_filename = f"{uuid.uuid4().hex}{extension}"
    destination = upload_dir / safe_filename

    with open(destination, "wb") as f:
        f.write(file_bytes)

    return str(destination)


def process_essay_upload(
    db: Session, user_id: int, file_bytes: bytes, original_filename: str
) -> Essay:
    """
    Full upload pipeline: size check -> save to disk -> extract text ->
    create DB record. Raises EssayUploadError with a user-facing message
    on any failure.
    """
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise EssayUploadError(
            f"File exceeds the {settings.max_upload_size_mb}MB upload limit."
        )
    if len(file_bytes) == 0:
        raise EssayUploadError("Uploaded file is empty.")

    saved_path = save_uploaded_file(file_bytes, original_filename)

    try:
        raw_text = extract_text(saved_path, original_filename)
    except Exception as e:
        # Re-raise as our own error type so the route layer has one
        # consistent exception to catch, regardless of which parser failed.
        raise EssayUploadError(str(e)) from e

    word_count = len(raw_text.split())
    extension = pathlib.Path(original_filename).suffix.lower().lstrip(".")

    essay = Essay(
        user_id=user_id,
        title=pathlib.Path(original_filename).stem,
        original_filename=original_filename,
        file_type=extension,
        raw_text=raw_text,
        word_count=word_count,
    )
    db.add(essay)
    db.commit()
    db.refresh(essay)
    return essay
