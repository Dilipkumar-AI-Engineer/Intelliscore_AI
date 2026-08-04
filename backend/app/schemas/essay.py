from datetime import datetime

from pydantic import BaseModel


class EssayResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    word_count: int
    created_at: datetime
    overall_score: float | None = None
    analyzed_at: datetime | None = None

    class Config:
        from_attributes = True


class EssayDetailResponse(EssayResponse):
    """Includes the full extracted text -- used for the single-essay view,
    not the list view (keeps list responses lightweight)."""
    raw_text: str


class SubScoreDetail(BaseModel):
    score: float
    explanation: str


class EssayAnalysisResponse(BaseModel):
    """Full analysis result: scores plus the raw Module 1/2 feature
    breakdown, for the Detailed Analysis view."""
    essay_id: int
    overall_score: float
    sub_scores: dict[str, SubScoreDetail]
    features: dict  # raw output of extract_features(), for charts/detail views
