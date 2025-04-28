import os
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.qa_history import QAHistory
from app.models.video import Video
from app.schemas.qa import QuestionCreate
from app.db.base import chroma_client
from typing import Tuple, List, Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QAService:
    def __init__(self, db: AsyncSession):
        logger.info("Initializing QAService")
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        self.db = db
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            chunk_size=1000
        )
        self.llm = ChatOpenAI(
            temperature=0,
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.output_parser = StrOutputParser()
        
        # Create debug directory if it doesn't exist
        os.makedirs("debug_qa", exist_ok=True)

    async def debug_collection(self, video_id: UUID) -> None:
        """Debug function to check ChromaDB collection state."""
        collection = await self.get_video_collection(video_id)
        if not collection:
            logger.error("Collection not found")
            return
            
        # Get collection info
        collection_info = collection.get()
        
        debug_content = f"""
{'='*80}
DEBUG INFO - ChromaDB Collection State
{'='*80}

VIDEO ID: {video_id}
TIMESTAMP: {datetime.now().isoformat()}
COLLECTION NAME: {collection.name}

Number of documents: {len(collection_info['ids'])}

Documents and metadata:
"""
        
        for i, (doc, meta) in enumerate(zip(collection_info['documents'], collection_info['metadatas'])):
            debug_content += f"\n--- Document {i+1} ---\n"
            debug_content += f"Metadata: {meta}\n"
            debug_content += f"Content:\n{doc}\n"
            debug_content += "-" * 40 + "\n"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_qa/collection_debug_{video_id}_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(debug_content)
        logger.info(f"Collection debug information saved to {filename}")

    def _save_debug_info(self, video_id: UUID, question: str, context: str, answer: str) -> None:
        """Save debug information to a file for analysis."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_qa/qa_debug_{video_id}_{timestamp}.txt"
        
        debug_content = f"""
{'='*80}
DEBUG INFO - Question/Answer Session
{'='*80}

VIDEO ID: {video_id}
TIMESTAMP: {datetime.now().isoformat()}

QUESTION:
{question}

{'='*80}
CONTEXT:
{context}

{'='*80}
ANSWER:
{answer}
{'='*80}
"""
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(debug_content)
        logger.info(f"Debug information saved to {filename}")

    async def get_video_collection(self, video_id: UUID):
        result = await self.db.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            logger.warning(f"Video not found: {video_id}")
            return None
        logger.info(f"Retrieved video collection: {video.chroma_collection_id}")
        return chroma_client.get_collection(name=video.chroma_collection_id)

    def _format_context(self, documents: List[str], metadatas: List[Dict[str, Any]]) -> str:
        """Format the context by combining document content with their metadata."""
        context_parts = []
        for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
            # Add metadata information if available
            timestamp = meta.get('timestamp', 'N/A')
            chunk_index = meta.get('chunk_index', i)
            
            # Format the segment header
            header = f"\n{'='*50}\n"
            header += f"SEGMENT {chunk_index}"
            if timestamp != 'N/A':
                header += f" (Timestamp: {timestamp})"
            header += f"\n{'='*50}\n"
            
            # Add the formatted content
            context_parts.append(f"{header}\n{doc.strip()}\n")
        
        formatted_context = "\n".join(context_parts)
        logger.info(f"Formatted context ({len(documents)} segments):\n{formatted_context}")
        return formatted_context

    async def ask_question(self, question_in: QuestionCreate) -> QAHistory:
        try:
            logger.info(f"Processing question: {question_in.question}")
            
            # Debug collection state
            await self.debug_collection(question_in.video_id)
            
            # Get video collection
            collection = await self.get_video_collection(question_in.video_id)
            if not collection:
                raise ValueError("Video not found")

            # Get collection info
            collection_info = collection.get()
            logger.info(f"Collection size: {len(collection_info['ids'])} documents")

            # Generate embeddings for the question
            question_embedding = self.embeddings.embed_query(question_in.question)
            logger.info("Generated question embedding")

            # Search for relevant context using similarity search
            results = collection.query(
                query_embeddings=[question_embedding],
                n_results=3,
                include=["documents", "metadatas"]
            )
            
            logger.info(f"Found {len(results['documents'][0])} relevant documents")

            # Format context with metadata
            context = self._format_context(
                results["documents"][0],
                results["metadatas"][0]
            ) if results["documents"] else ""

            if not context:
                logger.warning("No context found for the question")
                context = "Aucun contexte trouvé dans la vidéo."

            # Define the prompt template
            template = """
            Tu es un assistant spécialisé dans la réponse aux questions sur des vidéos.
            Utilise uniquement le contexte fourni pour répondre à la question.
            Si tu ne peux pas répondre à la question avec le contexte donné, réponds "Je ne peux pas répondre à cette question avec le contexte disponible."
            
            Le contexte est divisé en segments numérotés. Tu peux te référer à ces segments dans ta réponse si nécessaire.
            Si tu cites un segment spécifique, indique son numéro entre crochets, par exemple: [Segment 1].

            Contexte:
            {context}

            Question: {question}

            Réponse:"""

            # Create the prompt
            prompt = ChatPromptTemplate.from_template(template)

            # Create the chain
            chain = (
                {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | self.output_parser
            )

            # Get the answer
            answer = await chain.ainvoke({
                "context": context,
                "question": question_in.question
            })
            
            logger.info(f"Generated answer: {answer}")
            
            # Save debug information
            self._save_debug_info(question_in.video_id, question_in.question, context, answer)

            # Save to history
            qa_history = QAHistory(
                video_id=question_in.video_id,
                question=question_in.question,
                answer=answer,
                context=context
            )
            self.db.add(qa_history)
            await self.db.commit()
            await self.db.refresh(qa_history)
            
            return qa_history

        except Exception as e:
            logger.error(f"Error in ask_question: {str(e)}", exc_info=True)
            raise

    async def get_video_history(self, video_id: UUID) -> list[QAHistory]:
        result = await self.db.execute(
            select(QAHistory)
            .where(QAHistory.video_id == video_id)
            .order_by(QAHistory.created_at.desc())
        )
        return result.scalars().all()

    async def askQuestion(self, video_id: UUID, question: str) -> Tuple[str, float]:
        """
        Temporary implementation of question answering
        Returns a tuple of (answer, confidence)
        """
        # TODO: Implement actual RAG-based Q&A
        return "reponse", 0.95 