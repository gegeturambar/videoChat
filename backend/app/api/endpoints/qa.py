from fastapi import APIRouter, HTTPException
from typing import Dict
from uuid import UUID
from app.schemas.qa import QuestionRequest, QuestionResponse
from app.services.qa_service import qa_service

router = APIRouter()

@router.post("/videos/{video_id}/qa", response_model=QuestionResponse)
async def ask_question(video_id: string, question: QuestionRequest):
    """
    Process a question about a video using the QA service
    """
    answer, confidence = await qa_service.askQuestion(video_id, question.question)
    
    return QuestionResponse(
        answer=answer,
        confidence=str(confidence)
    ) 