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
from app.schemas.essay import (
    EssayAnalysisResponse,
    EssayCompareRequest,
    EssayCompareResponse,
    EssayDetailResponse,

    EssayResponse,
    EssayUpdateRequest,
    OrganizeEssayRequest,
    OrganizeEssayResponse,
    PromptAssistRequest,
    PromptAssistResponse,
    StructureDetectionResponse,
    TextPasteUploadRequest,
)
from app.services.analysis_service import (
    AnalysisError,
    analyze_essay,
    detect_essay_structure,
    organize_essay_text,
)
from app.services.chat_service import ChatMentorService
from app.services.essay_service import EssayUploadError, process_essay_upload, process_text_paste

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


@router.post("/upload-text", response_model=EssayResponse, status_code=status.HTTP_201_CREATED)
def upload_text_essay(
    req: TextPasteUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Method 2: Upload essay via direct text copy/paste."""
    try:
        essay = process_text_paste(db, current_user.id, req.text, req.title)
    except EssayUploadError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return essay


@router.post("/detect-structure", response_model=StructureDetectionResponse)
def detect_structure_endpoint(
    req: OrganizeEssayRequest,
    current_user: User = Depends(get_current_user),
):
    """Automatic Essay Structure Detection."""
    if not req.raw_text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Essay text cannot be empty.")
    res = detect_essay_structure(req.raw_text)
    return res


@router.post("/organize-text", response_model=OrganizeEssayResponse)
def organize_text_endpoint(
    req: OrganizeEssayRequest,
    current_user: User = Depends(get_current_user),
):
    """Smart Essay Formatting Before/After."""
    if not req.raw_text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Essay text cannot be empty.")
    res = organize_essay_text(req.raw_text)
    return res


@router.post("/assist-prompt", response_model=PromptAssistResponse)
def assist_prompt_endpoint(
    req: PromptAssistRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Method 4: Prompt-based AI Writing Assistance."""
    chat_res = ChatMentorService.generate_response(
        db=db,
        user_id=current_user.id,
        message=f"Writing prompt assistance request: '{req.prompt}'. Essay context: '{req.essay_text or 'None'}'",
    )
    outline = [
        "1. Introduction: Hook & Clear Thesis Statement",
        "2. Main Body Paragraph 1: Primary Claim with Concrete Evidence",
        "3. Main Body Paragraph 2: Secondary Supporting Claim & Analysis",
        "4. Counterargument & Rebuttal: Addressing Opposing Perspectives",
        "5. Conclusion: Synthesizing Key Findings & Broader Implications",
    ]
    return {
        "reply": chat_res["reply"],
        "suggested_structure": outline,
        "model": chat_res.get("model", "Gemini AI / RAG Engine"),
    }



@router.get("/", response_model=list[EssayResponse])
def list_essays(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List essays scoped by user identity: students and regular teachers see their own essays; demo teacher and admins see system showcase essays."""
    user_role = (current_user.role or "student").lower()
    email_lower = (current_user.email or "").lower().strip()

    if user_role in ["admin", "administrator"] or email_lower in ["priya@college.edu", "teacher@intelliscore.edu"]:
        return db.query(Essay).order_by(Essay.created_at.desc()).all()

    return (
        db.query(Essay)
        .filter(Essay.user_id == current_user.id)
        .order_by(Essay.created_at.desc())
        .all()
    )


@router.get("/class-analytics")
def get_class_analytics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Class analytics for Teacher role."""
    user_role = (current_user.role or "student").lower()
    if user_role not in ["teacher", "admin", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher or Admin role required.")

    email_lower = (current_user.email or "").lower().strip()
    is_demo_teacher = email_lower in ["priya@college.edu", "teacher@intelliscore.edu"] or user_role in ["admin", "administrator"]

    if is_demo_teacher:
        total_students = db.query(User).filter(User.role == "student").count()
        essays = db.query(Essay).filter(Essay.overall_score.isnot(None)).all()
        all_class_essays = db.query(Essay).all()
    else:
        total_students = 0
        essays = db.query(Essay).filter(Essay.user_id == current_user.id, Essay.overall_score.isnot(None)).all()
        all_class_essays = db.query(Essay).filter(Essay.user_id == current_user.id).all()
    
    if not essays:
        return {
            "total_students": total_students,
            "essays_submitted": len(all_class_essays),
            "essays_evaluated": 0,
            "class_average": 0.0,
            "highest_score": 0.0,
            "lowest_score": 0.0,
            "recent_submissions": [],
            "common_weaknesses": ["Grammar consistency", "Vocabulary variety", "Paragraph coherence"],
        }

    scores = [e.overall_score for e in essays if e.overall_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    high_score = max(scores) if scores else 0.0
    low_score = min(scores) if scores else 0.0

    recent_query = db.query(Essay)
    if not is_demo_teacher:
        recent_query = recent_query.filter(Essay.user_id == current_user.id)

    recent = recent_query.order_by(Essay.created_at.desc()).limit(10).all()
    submission_list = []
    for r in recent:
        owner = db.query(User).filter(User.id == r.user_id).first()
        submission_list.append({
            "id": r.id,
            "title": r.title,
            "student_name": owner.full_name if owner else "Student",
            "score": r.overall_score,
            "submitted_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "total_students": max(total_students, 1 if is_demo_teacher else 0),
        "essays_submitted": len(all_class_essays),
        "essays_evaluated": len(essays),
        "class_average": avg_score,
        "highest_score": high_score,
        "lowest_score": low_score,
        "recent_submissions": submission_list,
        "common_weaknesses": ["Passive voice overuse", "Sentence structure complexity", "Transition clarity"],
    }


@router.get("/platform-stats")
def get_platform_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Platform system stats for Admin role."""
    user_role = (current_user.role or "student").lower()
    if user_role not in ["admin", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")

    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    total_admins = db.query(User).filter(User.role.in_(["admin", "administrator"])).count()
    total_essays = db.query(Essay).count()
    evaluated_essays = db.query(Essay).filter(Essay.overall_score.isnot(None)).count()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_admins": total_admins,
        "total_essays": total_essays,
        "total_analyses": evaluated_essays,
        "system_health": "100% Operational",
        "ai_model_status": "Active (Gemini 1.5 Flash)",
    }


@router.post("/compare", response_model=EssayCompareResponse)
def compare_essays_endpoint(
    request: EssayCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_role = (current_user.role or "student").lower()
    if not request.essay_ids or len(request.essay_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 essay IDs are required for comparison.",
        )

    essays = db.query(Essay).filter(Essay.id.in_(request.essay_ids)).all()

    if user_role not in ["teacher", "admin", "administrator"]:
        essays = [e for e in essays if e.user_id == current_user.id]

    if len(essays) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find at least 2 accessible essays for comparison.",
        )

    try:
        result = compare_essays(db, essays)
    except AnalysisError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return result


@router.get("/{essay_id}", response_model=EssayDetailResponse)
def get_essay(
    essay_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_role = (current_user.role or "student").lower()
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if essay is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")
    
    if user_role not in ["teacher", "admin", "administrator"] and essay.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")
    return essay


@router.post("/{essay_id}/analyze", response_model=EssayAnalysisResponse)
def analyze_essay_endpoint(
    essay_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_role = (current_user.role or "student").lower()
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if essay is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")

    if user_role not in ["teacher", "admin", "administrator"] and essay.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")

    try:
        result = analyze_essay(db, essay)
    except AnalysisError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return result


@router.put("/{essay_id}", response_model=EssayAnalysisResponse)
def update_and_reanalyze_essay(
    essay_id: int,
    req: EssayUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update essay raw text and dynamically re-trigger AI analysis pipeline."""
    user_role = (current_user.role or "student").lower()
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if essay is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")

    if user_role not in ["teacher", "admin", "administrator"] and essay.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essay not found")

    essay.raw_text = req.raw_text
    words = [w for w in req.raw_text.split() if w.strip()]
    essay.word_count = len(words)
    if req.title:
        essay.title = req.title

    db.add(essay)
    db.commit()
    db.refresh(essay)

    try:
        result = analyze_essay(db, essay)
    except AnalysisError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return result



