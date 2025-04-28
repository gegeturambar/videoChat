from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate
import uuid

def get_video(db: Session, video_id: uuid.UUID) -> Optional[Video]:
    return db.query(Video).filter(Video.id == video_id).first()

def get_videos(db: Session, skip: int = 0, limit: int = 100) -> List[Video]:
    return db.query(Video).offset(skip).limit(limit).all()

def create_video(db: Session, video: VideoCreate) -> Video:
    db_video = Video(
        title=video.title,
        url=video.url,
        status="pending",  # État initial
        chroma_collection_id=str(uuid.uuid4())  # Générer un ID unique pour la collection
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video(db: Session, video_id: uuid.UUID, video: VideoUpdate) -> Optional[Video]:
    db_video = get_video(db, video_id)
    if db_video is None:
        return None
    
    for var, value in vars(video).items():
        setattr(db_video, var, value)
    
    db.commit()
    db.refresh(db_video)
    return db_video

def delete_video(db: Session, video_id: uuid.UUID) -> bool:
    db_video = get_video(db, video_id)
    if db_video is None:
        return False
    
    db.delete(db_video)
    db.commit()
    return True 