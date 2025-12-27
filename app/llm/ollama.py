"""
Ollama LLM integration for Teslas.ai (LangChain-native).

Features:
- Official ChatOllama integration
- No direct HTTP calls
- Multi-agent friendly
- Cached per (model, temperature)
- Future-proof against Ollama API changes
"""

from functools import lru_cache
from typing import Optional

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


SYSTEM_IDENTITY = """
You are Teslas.ai, a scientific multi-agent assistant for applied mathematics
and data science research.

Rules:
- Be rigorous and explicit.
- State assumptions clearly.
- Avoid hallucinations.
- Prefer mathematical clarity over verbosity.
- Cite sources when relevant.
"""


# -------------------------------------------------
# Internal cached factory (DO NOT use directly)
# -------------------------------------------------

@lru_cache
def _get_llm_cached(model: str, temperature: float) -> ChatOllama:
    """
    Internal cached LLM factory.

    Cache key = (model, temperature)
    This allows different agents to use different temperatures safely.
    """
    logger.info(
        "Initializing Ollama Chat LLM",
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature,
    )

    llm = ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature,
    )

    # Prime the model with Teslas.ai identity (best-effort)
    try:
        llm.invoke([SystemMessage(content=SYSTEM_IDENTITY)])
    except Exception as e:
        logger.warning(
            "Could not prime Ollama system message",
            error=str(e),
        )

    return llm


# -------------------------------------------------
# Public API (used by agents)
# -------------------------------------------------

def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> ChatOllama:
    """
    Return a cached ChatOllama instance.

    Parameters
    ----------
    model : str, optional
        Ollama model name (default: settings.OLLAMA_MODEL)
    temperature : float, optional
        Sampling temperature (default: settings.TEMPERATURE)

    Returns
    -------
    ChatOllama
        Cached LLM instance
    """
    return _get_llm_cached(
        model or settings.OLLAMA_MODEL,
        temperature if temperature is not None else settings.TEMPERATURE,
    )
