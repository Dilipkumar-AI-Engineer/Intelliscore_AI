"""
Essay-Specific Gemini AI Chatbot Mentor API endpoints.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.chat_service import ChatMentorService

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="Student chat message or prompt")
    essay_id: Optional[str] = Field(None, description="Optional active essay ID for RAG context")
    history: Optional[List[Dict[str, Any]]] = Field(default=[], description="Chat conversation history")
    api_key: Optional[str] = Field(None, description="Optional client-provided Gemini API key")


class ChatMessageResponse(BaseModel):
    reply: str
    sources: List[str]
    model: str
    deduplicated: bool = Field(default=True, description="Indicates anti-duplication and anti-repetition guard pass")


@router.post("/mentor", response_model=ChatMessageResponse)
@router.post("/gemini-mentor", response_model=ChatMessageResponse)
def get_mentor_response(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns live Essay-Specific Gemini AI Writing Mentor conversational response with anti-duplication & RAG context.
    """
    res = ChatMentorService.generate_response(
        db=db,
        user_id=current_user.id,
        message=payload.message,
        essay_id=payload.essay_id,
        history=payload.history,
        custom_api_key=payload.api_key,
    )
    res["deduplicated"] = True
    return ChatMessageResponse(**res)
