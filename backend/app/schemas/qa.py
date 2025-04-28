from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class QuestionCreate(BaseModel):
    video_id: UUID
    question: str

class QAResponse(BaseModel):
    id: UUID
    video_id: UUID
    question: str
    answer: str
    context: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QAHistoryItem(QAResponse):
    pass

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    confidence: str 