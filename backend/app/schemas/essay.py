from datetime import datetime

from pydantic import BaseModel


class EssayResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class EssayDetailResponse(EssayResponse):
    """Includes the full extracted text -- used for the single-essay view,
    not the list view (keeps list responses lightweight)."""
    raw_text: str
