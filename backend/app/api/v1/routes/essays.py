"""
Essay routes: upload, list, and retrieve essays. All protected -- a user
must be logged in (Module 5's JWT auth) to use any of these.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.essay import Essay
from app.models.user import User
from app.schemas.essay import EssayAnalysisResponse, EssayDetailResponse, EssayResponse
from app.services.analysis_service import AnalysisError, analyze_essay
from app.services.essay_service import EssayUploadError, process_essay_upload

router = APIRouter(prefix="/api/v1/essays", tags=["essays"])


@router.post("/upload", response_model=EssayResponse, status_code=status.HTTP_201_CREATED)
async def upload_essay(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()
    try:
        essay = process_essay_upload(db, current_user.id, file_bytes, file.filename)
    except EssayUploadError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return essay


@router.get("/", response_model=list[EssayResponse])
def list_essays(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List the CURRENT user's essays only -- scoped by user_id, never all essays."""
    return (
        db.query(Essay)
        .filter(Essay.user_id == current_user.id)
        .order_by(Essay.created_at.desc())
        .all()
    )


@router.get("/{essay_id}", response_model=EssayDetailResponse)
def get_essay(
    essay_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if essay is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")
    if essay.user_id != current_user.id:
        # 404, not 403 -- don't reveal that an essay with this ID exists
        # but belongs to someone else (same principle as Module 5's
        # identical login-error-message decision).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")
    return essay


@router.post("/{essay_id}/analyze", response_model=EssayAnalysisResponse)
def analyze_essay_endpoint(
    essay_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if essay is None or essay.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")

    try:
        result = analyze_essay(db, essay)
    except AnalysisError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return result
