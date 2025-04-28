from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import video as video_service
from app.schemas.video import Video, VideoCreate, VideoUpdate
from uuid import UUID

router = APIRouter()

@router.get("/videos", response_model=List[Video])
async def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    videos = await video_service.get_videos(db, skip=skip, limit=limit)
    return videos

@router.post("/videos", response_model=Video)
async def create_video(video: VideoCreate, db: Session = Depends(get_db)):
    video_obj, error_msg = await video_service.create_video(db=db, video=video)
    if error_msg:
        raise HTTPException(status_code=400, detail=error_msg)
    return video_obj

@router.get("/videos/{video_id}", response_model=Video)
async def read_video(video_id: UUID, db: Session = Depends(get_db)):
    db_video = await video_service.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.put("/videos/{video_id}", response_model=Video)
async def update_video(video_id: UUID, video: VideoUpdate, db: Session = Depends(get_db)):
    db_video, error_msg = await video_service.update_video(db, video_id=video_id, video=video)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    if error_msg:
        raise HTTPException(status_code=400, detail=error_msg)
    return db_video

@router.delete("/videos/{video_id}")
async def delete_video(video_id: UUID, db: Session = Depends(get_db)):
    success = await video_service.delete_video(db, video_id=video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"status": "success"} 