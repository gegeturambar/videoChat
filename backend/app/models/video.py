from sqlalchemy import Column, String, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    status = Column(String, nullable=False)
    chroma_collection_id = Column(String, nullable=False)
    transcription = Column(Text, nullable=True)  # New field for storing transcription
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 