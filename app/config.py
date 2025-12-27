"""Configuration management for Teslas.ai scientific assistant."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    EMBEDDINGS_DIR: Path = DATA_DIR / "embeddings"
    CACHE_DIR: Path = DATA_DIR / "cache"
    CHROMA_DIR: Path = PROJECT_ROOT / "chroma"

    # LLM Configuration
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "mistral"  # Can be changed to neural-chat, dolphin-mixtral, etc.
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Hugging Face sentence-transformers model
    
    # ChromaDB Configuration
    CHROMA_COLLECTION_NAME: str = "scientific_documents"
    CHROMA_PERSIST_DIR: Path = CHROMA_DIR / "scientific_db"
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    RERANK_TOP_K: int = 3
    
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Streamlit Configuration
    STREAMLIT_THEME: str = "dark"
    STREAMLIT_PAGE_TITLE: str = "Teslas.ai - Scientific Assistant"
    
    # Search Configuration
    DUCKDUCKGO_MAX_RESULTS: int = 10
    DUCKDUCKGO_TIMEOUT: int = 10
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Agent Configuration
    AGENT_TIMEOUT: int = 300  # 5 minutes
    MAX_ITERATIONS: int = 10
    TEMPERATURE: float = 0.3  # Lower = more deterministic
    
    # Feature Flags
    ENABLE_WEB_SEARCH: bool = True
    ENABLE_RAG: bool = True
    ENABLE_MEMORY: bool = True
    DEBUG_MODE: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get or create settings instance."""
    return Settings()


# Create settings instance
settings = get_settings()

# Ensure directories exist
settings.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
