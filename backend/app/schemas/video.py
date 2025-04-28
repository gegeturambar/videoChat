from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID

class VideoBase(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    transcription: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoUpdate(VideoBase):
    pass

class VideoInDB(VideoBase):
    id: UUID
    status: str
    chroma_collection_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Video(VideoInDB):
    pass 