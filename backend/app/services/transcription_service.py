from functools import partial
import re
import logging
import os
import tempfile
import yt_dlp
import whisper
import ssl
import certifi
import asyncio
from typing import Tuple, Optional, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration SSL plus robuste
if os.environ.get('PYTHONHTTPSVERIFY', '') == '0':
    ssl._create_default_https_context = ssl._create_unverified_context
    logger.warning("SSL certificate verification is disabled")
else:
    ssl._create_default_https_context = ssl.create_default_context
    ssl._create_default_https_context().load_verify_locations(certifi.where())
    logger.info("SSL certificate verification is enabled")

class TranscriptionService:
    def __init__(self):
        try:
            logger.info("Initializing Whisper model...")
            self.model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise

    def validate_youtube_url(self, url: str) -> bool:
        """Validate if the URL is a valid YouTube URL"""
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(re.match(youtube_regex, url))

    async def download_audio(self, url: str) -> str:
        try:
            # Créer un dossier temporaire unique
            temp_dir = Path(tempfile.mkdtemp())
            logger.info(f"Created temporary directory: {temp_dir}")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(temp_dir / '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'nocheckcertificate': os.environ.get('PYTHONHTTPSVERIFY', '') == '0',
                'ignoreerrors': False,
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
                },
                'prefer_insecure': os.environ.get('PYTHONHTTPSVERIFY', '') == '0',
                'legacy_server_connect': True
            }
            
            return await self._download_with_ytdl(url, ydl_opts)
        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            if temp_dir.exists():
                try:
                    for file in temp_dir.glob('*'):
                        file.unlink()
                    temp_dir.rmdir()
                except Exception as cleanup_error:
                    logger.warning(f"Error cleaning up temporary directory: {cleanup_error}")
            raise

    async def _download_with_ytdl(self, url: str, ydl_opts: dict) -> str:
        try:
            # Exécuter yt-dlp dans un thread séparé pour ne pas bloquer
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading audio from URL: {url}")
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                output_template = ydl_opts['outtmpl']
                if isinstance(output_template, dict):
                    output_template = output_template['default']
                output_dir = Path(os.path.dirname(output_template))
                video_id = info['id']
                audio_path = output_dir / f"{video_id}.wav"
                logger.info(f"Audio downloaded successfully to: {audio_path}")
                return str(audio_path)
        except Exception as e:
            logger.error(f"Error in _download_with_ytdl: {str(e)}")
            raise

    async def transcribe_youtube_video(self, url: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        temp_dir = None
        try:
            # Validate URL first
            if not self.validate_youtube_url(url):
                logger.error(f"Invalid YouTube URL: {url}")
                return None, "URL YouTube invalide"

            # Télécharger l'audio
            audio_path = await self.download_audio(url)
            temp_dir = Path(audio_path).parent
            
            # Transcrire dans un thread séparé
            logger.info("Starting transcription...")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self.model.transcribe(audio_path))
            logger.info("Transcription completed successfully")
            
            # Retourner la transcription
            if result and "text" in result:
                return {"url": url, "transcription": result["text"]}, None
            else:
                error_msg = "La transcription a échoué. Aucun texte n'a été généré."
                return None, error_msg

        except Exception as e:
            logger.error(f"Error in transcribe_youtube_video: {str(e)}", exc_info=True)
            error_msg = f"La transcription a échoué: {str(e)}"
            return None, error_msg
            
        finally:
            # Nettoyer les fichiers temporaires
            if temp_dir and temp_dir.exists():
                try:
                    for file in temp_dir.glob('*'):
                        file.unlink()
                    temp_dir.rmdir()
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Error cleaning up temporary files: {cleanup_error}")

# Create a singleton instance
transcription_service = TranscriptionService() 