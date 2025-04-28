from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.base import get_db
from app.schemas.qa import QuestionCreate, QAResponse, QAHistoryItem
from app.services.qa_service import QAService

router = APIRouter()


@router.get("/askeu")
async def askeu_question(
    db: AsyncSession = Depends(get_db)
):
    return "Hello World"

@router.post("/ask", response_model=QAResponse)
async def ask_question(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    qa_service = QAService(db)
    try:
        return await qa_service.ask_question(question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/history/{video_id}", response_model=List[QAHistoryItem])
async def get_video_qa_history(
    video_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    qa_service = QAService(db)
    return await qa_service.get_video_history(video_id) 