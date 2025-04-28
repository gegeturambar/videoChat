import asyncio
import logging
import os
import sys
from pathlib import Path

# Ajout du chemin du backend au PYTHONPATH de manière plus robuste
current_dir = Path(__file__).parent.absolute()
backend_path = current_dir / "backend"
sys.path.append(str(backend_path))

from app.services.transcription_service import TranscriptionService

# Configuration des logs avec plus de détails
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def test():
    try:
        logger.info("Starting transcription test...")
        backend_path = str(Path(__file__).parent / "backend")
        logger.info(f"Backend path: {backend_path}")
        
        # Test URL (Me at the zoo - First YouTube video)
        url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        logger.info(f"Testing transcription with URL: {url}")
        
        logger.info("Initializing transcription service...")
        transcription_service = TranscriptionService()
        
        # Call the transcribe function and await its result
        result, error = await transcription_service.transcribe_youtube_video(url)
        
        if error:
            logger.error(f"Transcription failed with error: {error}")
            return False
            
        if not result or "transcription" not in result:
            logger.error("Invalid transcription result format")
            return False
            
        logger.info("Transcription successful!")
        logger.info(f"Transcription: {result['transcription']}")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error during test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run the async test function
    success = asyncio.run(test())
    sys.exit(0 if success else 1) 