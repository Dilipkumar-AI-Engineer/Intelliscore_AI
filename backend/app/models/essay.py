"""
Essay table definition. Links each uploaded essay to the user who
uploaded it (foreign key), so Module 5's auth system and this module
work together: only a logged-in user can upload, and essays are scoped
per-user.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Essay(Base):
    __tablename__ = "essays"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf/docx/txt/png/jpg
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Analysis results (Module 8) -- nullable, since an essay may be
    # uploaded but not yet analyzed. Populated by POST /essays/{id}/analyze.
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    grammar_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    vocabulary_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    coherence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    argument_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    readability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
