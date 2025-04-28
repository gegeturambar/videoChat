from uuid import UUID
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate
from app.db.base import chroma_client
from typing import List
from app.services.transcription_service import transcription_service
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class VideoProcessingError(Exception):
    """Custom exception for video processing errors"""
    pass

class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            chunk_size=1000
        )

    async def _update_chroma_collection(self, video: Video) -> None:
        """Update ChromaDB collection with video transcription chunks"""
        try:
            logger.info(f"Updating ChromaDB collection for video {video.id}")
            
            # Get or create collection
            collection = chroma_client.get_or_create_collection(
                name=video.chroma_collection_id,
                metadata={"video_id": str(video.id)}
            )
            
            # Clear existing documents if any
            try:
                collection.delete(where={})
                logger.info("Cleared existing documents from collection")
            except Exception as e:
                logger.warning(f"Error clearing collection (might be empty): {str(e)}")
            
            if not video.transcription:
                logger.warning("No transcription available for indexing")
                return
                
            # Split transcription into chunks
            chunks = self.text_splitter.split_text(video.transcription)
            logger.info(f"Split transcription into {len(chunks)} chunks")
            
            if not chunks:
                logger.warning("No chunks generated from transcription")
                return
                
            try:
                # Generate embeddings for all chunks
                embeddings = self.embeddings.embed_documents(chunks)
                logger.info(f"Generated {len(embeddings)} embeddings")
                
                # Prepare metadata for each chunk
                metadatas = [
                    {
                        "source": "transcription",
                        "video_id": str(video.id),
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    } 
                    for i in range(len(chunks))
                ]
                
                # Add chunks to collection with metadata and embeddings
                collection.add(
                    documents=chunks,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=[f"chunk_{i}" for i in range(len(chunks))]
                )
                logger.info(f"Successfully added {len(chunks)} chunks to ChromaDB")
                
                # Verify the update
                collection_info = collection.get()
                logger.info(f"Collection now contains {len(collection_info['ids'])} documents")
                
            except Exception as e:
                logger.error(f"Error adding chunks to ChromaDB: {str(e)}")
                raise VideoProcessingError(f"Error adding chunks to ChromaDB: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error updating ChromaDB collection: {str(e)}", exc_info=True)
            raise VideoProcessingError(f"Error updating ChromaDB collection: {str(e)}")

    async def process_transcription(self, video: Video) -> None:
        """Process video transcription"""
        try:
            result, error = await transcription_service.transcribe_youtube_video(video.url)
            if error:
                video.status = "failed"
                raise VideoProcessingError(error)
                
            if result and "transcription" in result:
                video.transcription = result["transcription"]
                video.status = "completed"
                # Update ChromaDB collection with transcription chunks
                await self._update_chroma_collection(video)
            else:
                video.status = "failed"
                raise VideoProcessingError("La transcription a échoué. Vérifiez que l'URL est valide et que la vidéo est accessible.")
                
        except Exception as e:
            video.status = "failed"
            error_msg = str(e)
            logger.error(f"Error during transcription: {error_msg}")
            raise VideoProcessingError(f"Erreur lors de la transcription: {error_msg}")

    async def create_video(self, video_in: VideoCreate) -> Video:
        try:
            # Create ChromaDB collection
            collection_id = f"video_{uuid.uuid4()}"
            chroma_client.create_collection(name=collection_id)
            
            # Create video in PostgreSQL
            db_video = Video(
                url=video_in.url,
                title=video_in.title,
                description=video_in.description,
                status="processing",  # Changed to processing while we transcribe
                chroma_collection_id=collection_id
            )
            self.db.add(db_video)
            await self.db.commit()
            await self.db.refresh(db_video)

            # Process transcription
            await self.process_transcription(db_video)
            await self.db.commit()
            await self.db.refresh(db_video)
            
            return db_video
            
        except Exception as e:
            # If anything fails, ensure we clean up the ChromaDB collection
            try:
                chroma_client.delete_collection(name=collection_id)
            except:
                pass
            raise

    async def get_video(self, video_id: UUID) -> Video:
        result = await self.db.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo non trouvée")
        return video

    async def update_video(self, video_id: UUID, video_in: VideoUpdate) -> Video:
        video = await self.get_video(video_id)
            
        # Update fields
        for field, value in video_in.dict(exclude_unset=True).items():
            setattr(video, field, value)
        
        # If URL changed, reprocess transcription
        if "url" in video_in.dict(exclude_unset=True):
            video.status = "processing"
            await self.db.commit()
            await self.db.refresh(video)
            await self.process_transcription(video)
            
        await self.db.commit()
        await self.db.refresh(video)
        return video

    async def delete_video(self, video_id: UUID) -> bool:
        video = await self.get_video(video_id)
            
        # Delete ChromaDB collection
        try:
            chroma_client.delete_collection(name=video.chroma_collection_id)
        except Exception:
            logger.warning(f"Failed to delete ChromaDB collection for video {video_id}")
            
        # Delete from PostgreSQL
        await self.db.delete(video)
        await self.db.commit()
        return True

    async def get_videos(self, skip: int = 0, limit: int = 100) -> List[Video]:
        result = await self.db.execute(
            select(Video).offset(skip).limit(limit)
        )
        return result.scalars().all() 