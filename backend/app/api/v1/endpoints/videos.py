from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from uuid import UUID
from pydantic import BaseModel

from app.db.base import get_db
from app.schemas.video import Video, VideoCreate, VideoUpdate
from app.services.video_service import VideoService, VideoProcessingError
from app.services.transcription_service import transcription_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class TranscriptionRequest(BaseModel):
    url: str

class TranscriptionResponse(BaseModel):
    url: str
    transcription: str

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_video(
    request: TranscriptionRequest,
):
    """
    Transcrit une vidéo YouTube et retourne la transcription.
    """
    result, error = await transcription_service.transcribe_youtube_video(request.url)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return TranscriptionResponse(**result)

@router.post("/", response_model=Video)
async def create_video(
    video_in: VideoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crée une nouvelle vidéo"""
    try:
        video_service = VideoService(db)
        return await video_service.create_video(video_in)
    except VideoProcessingError as e:
        logger.error(f"Error creating video: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating video: {str(e)}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue s'est produite")

@router.get("/{video_id}", response_model=Video)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Récupère une vidéo par son ID"""
    try:
        video_service = VideoService(db)
        return await video_service.get_video(video_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue s'est produite")

@router.put("/{video_id}", response_model=Video)
async def update_video(
    video_id: UUID,
    video_in: VideoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Met à jour une vidéo"""
    try:
        video_service = VideoService(db)
        return await video_service.update_video(video_id, video_in)
    except VideoProcessingError as e:
        logger.error(f"Error updating video {video_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue s'est produite")

@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Supprime une vidéo"""
    try:
        video_service = VideoService(db)
        await video_service.delete_video(video_id)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue s'est produite")

@router.get("/", response_model=List[Video])
async def list_videos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Liste toutes les vidéos"""
    try:
        video_service = VideoService(db)
        return await video_service.get_videos(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Une erreur inattendue s'est produite") 