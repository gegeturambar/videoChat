from pydantic_settings import BaseSettings
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VideoQA API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Application settings
    APP_NAME: str = "VideoChat"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # PostgreSQL
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "videoqa"
    POSTGRES_PASSWORD: str = "videoqa_password"
    POSTGRES_DB: str = "videoqa"
    DATABASE_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # ChromaDB
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    CHROMA_AUTH_ENABLED: bool = False
    CHROMA_TENANT: str = "videochat"
    CHROMA_DATABASE: str = "videochat_db"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"  # Modèle par défaut
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"  # Modèle d'embedding par défaut

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    def get_chroma_client(self) -> chromadb.HttpClient:
        """
        Retourne un client ChromaDB configuré
        """
        return chromadb.HttpClient(
            host=self.CHROMA_HOST,
            port=self.CHROMA_PORT,
            ssl=False,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    

settings = Settings() 