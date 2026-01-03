"""Configuration management for Teslas.ai scientific assistant."""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic_settings import BaseSettings


class ExecutionMode(str, Enum):
    """Execution mode for controlling agent selection, RAG depth, and resource usage.
    
    FAST MODE:
    - Purpose: Quick scientific answers, exploratory analysis, daily usage
    - Constraints: Minimal latency, reduced agent execution, no deep review
    - Target: Few minutes maximum
    - Agents: Essential agents only (planner optional, writer enabled, reviewer/memory disabled)
    - RAG: Limited depth (top-k ≤ 15, final chunks ≤ 3)
    
    FULL MODE:
    - Purpose: Deep scientific research, high rigor, publication-grade output
    - Constraints: Maximum correctness, full traceability, complete workflow
    - Target: Long runtime acceptable (tens of minutes)
    - Agents: ALL agents enabled (planner, mathematician, numerical, literature, reviewer, writer, memory)
    - RAG: Maximum depth (top-k ≥ 30, final chunks ≤ 5, web search enabled)
    """
    FAST = "fast"
    FULL = "full"


class ModeConfig:
    """Configuration parameters for each execution mode.
    
    This class defines the exact behavior of FAST and FULL modes across all
    system components: agent selection, RAG parameters, LLM settings, and runtime limits.
    """
    
    # Agent participation by mode
    # True = enabled, False = disabled, "optional" = may be skipped based on plan
    AGENT_CONFIG: Dict[str, Dict[str, Any]] = {
        ExecutionMode.FAST: {
            "planner": "optional",  # Lightweight planning only
            "mathematician": "optional",  # Only if clearly mathematical
            "numerical": "optional",  # Only if clearly numerical
            "data_scientist": False,  # Disabled in FAST mode
            "literature": "optional",  # Quick search only
            "reviewer": False,  # Disabled - no deep review
            "writer": True,  # Always enabled (concise output)
            "memory": False,  # Disabled - no memory curation
        },
        ExecutionMode.FULL: {
            "planner": True,  # Full planning
            "mathematician": True,  # Always run if relevant
            "numerical": True,  # Always run if relevant
            "data_scientist": True,  # Full data analysis
            "literature": True,  # Comprehensive literature search
            "reviewer": True,  # Critical scientific review
            "writer": True,  # Detailed structured output
            "memory": True,  # Memory curation enabled
        },
    }
    
    # RAG parameters by mode
    RAG_CONFIG: Dict[str, Dict[str, Any]] = {
        ExecutionMode.FAST: {
            "faiss_top_k": 15,  # Initial retrieval limit
            "final_chunks": 3,  # Maximum chunks after reranking
            "rerank_enabled": True,  # Still use reranking for quality
            "context_compression": True,  # Compress context
            "web_search_enabled": False,  # No web search
        },
        ExecutionMode.FULL: {
            "faiss_top_k": 30,  # Broader initial retrieval
            "final_chunks": 5,  # More chunks for depth
            "rerank_enabled": True,  # Full reranking pipeline
            "context_compression": True,  # Compress but preserve detail
            "web_search_enabled": True,  # Enable web search if available
        },
    }
    
    # LLM parameters by mode
    LLM_CONFIG: Dict[str, Dict[str, Any]] = {
        ExecutionMode.FAST: {
            "temperature": 0.1,  # More deterministic
            "max_tokens": 2000,  # Shorter responses
            "timeout": 120,  # 2 minutes max per LLM call
        },
        ExecutionMode.FULL: {
            "temperature": 0.3,  # Balanced creativity/determinism
            "max_tokens": 4000,  # Longer detailed responses
            "timeout": 300,  # 5 minutes max per LLM call
        },
    }
    
    # Iteration limits by mode
    ITERATION_CONFIG: Dict[str, Dict[str, int]] = {
        ExecutionMode.FAST: {
            "max_iterations": 3,  # Limit iterations
            "max_agent_calls": 5,  # Limit total agent invocations
        },
        ExecutionMode.FULL: {
            "max_iterations": 10,  # Allow full workflow
            "max_agent_calls": 20,  # Allow comprehensive analysis
        },
    }
    
    @classmethod
    def get_agent_config(cls, mode: ExecutionMode) -> Dict[str, Any]:
        """Get agent configuration for specified mode."""
        return cls.AGENT_CONFIG[mode]
    
    @classmethod
    def get_rag_config(cls, mode: ExecutionMode) -> Dict[str, Any]:
        """Get RAG configuration for specified mode."""
        return cls.RAG_CONFIG[mode]
    
    @classmethod
    def get_llm_config(cls, mode: ExecutionMode) -> Dict[str, Any]:
        """Get LLM configuration for specified mode."""
        return cls.LLM_CONFIG[mode]
    
    @classmethod
    def get_iteration_config(cls, mode: ExecutionMode) -> Dict[str, int]:
        """Get iteration configuration for specified mode."""
        return cls.ITERATION_CONFIG[mode]
    
    @classmethod
    def is_agent_enabled(cls, mode: ExecutionMode, agent_name: str) -> bool:
        """Check if agent is enabled for specified mode.
        
        Returns:
            True if agent is enabled (always runs)
            False if agent is disabled (never runs)
            For 'optional' agents, caller must decide based on context
        """
        agent_status = cls.AGENT_CONFIG[mode].get(agent_name, False)
        if agent_status == "optional":
            # Caller must decide - return False as default but signal it's optional
            return False
        return bool(agent_status)
    
    @classmethod
    def is_agent_optional(cls, mode: ExecutionMode, agent_name: str) -> bool:
        """Check if agent is optional (may run based on plan)."""
        return cls.AGENT_CONFIG[mode].get(agent_name) == "optional"


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
    OLLAMA_MODEL: str = "phi"  # Can be changed to mistral, neural-chat, dolphin-mixtral, etc.
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
    
    # Execution Mode Configuration
    DEFAULT_EXECUTION_MODE: ExecutionMode = ExecutionMode.FAST
    
    # Agent Configuration (defaults - can be overridden by mode)
    AGENT_TIMEOUT: int = 300  # 5 minutes
    MAX_ITERATIONS: int = 10
    TEMPERATURE: float = 0.3  # Lower = more deterministic
    
    # Feature Flags
    ENABLE_WEB_SEARCH: bool = True
    ENABLE_RAG: bool = True
    ENABLE_MEMORY: bool = True
    DEBUG_MODE: bool = False
    
    def get_mode_config(self, mode: Optional[ExecutionMode] = None) -> ModeConfig:
        """Get configuration for specified execution mode.
        
        Parameters
        ----------
        mode : ExecutionMode, optional
            Execution mode (FAST or FULL). If None, uses DEFAULT_EXECUTION_MODE.
        
        Returns
        -------
        ModeConfig
            Mode configuration instance with all parameters
        """
        if mode is None:
            mode = self.DEFAULT_EXECUTION_MODE
        return ModeConfig()

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
