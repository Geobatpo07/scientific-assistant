"""Simple facade over Teslas.ai capabilities.

Provides: research, search, ingest
"""
from pathlib import Path
from typing import List, Optional

from app.agents.graph import create_orchestrator
from app.config import ExecutionMode
from app.tools.duckduckgo_search import create_searcher
from app.vectorstore.store import get_vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Assistant:
    """High-level interface for Teslas.ai."""

    def __init__(self) -> None:
        self._orchestrator = create_orchestrator()
        self._searcher = create_searcher()

    def research(
        self,
        query: str,
        agents: Optional[List[str]] = None,
        mode: ExecutionMode = ExecutionMode.FAST,
    ):
        """Run end-to-end research workflow and return context.
        
        Parameters
        ----------
        query : str
            Research question or query
        agents : list of str, optional
            Specific agents to use. If provided, runs selective mode.
            If None, runs full workflow based on execution mode.
        mode : ExecutionMode, optional
            Execution mode (FAST or FULL), defaults to FAST
            - FAST: Quick answers, minimal latency, reduced agents
            - FULL: Deep research, maximum rigor, all agents
        
        Returns
        -------
        ResearchContext
            Complete research context with all results
        """
        logger.info("Assistant.research", query=query, agents=agents, mode=mode.value)
        if agents:
            return self._orchestrator.run_research_selective(query, agents, mode)
        return self._orchestrator.run_research(query, mode)

    def search(self, query: str, search_type: str = "scientific", max_results: int = 10):
        """Perform web search with optional source type."""
        logger.info("Assistant.search", query=query, type=search_type, max=max_results)
        if search_type == "arxiv":
            results = self._searcher.search_arxiv(query)
        elif search_type == "scholar":
            results = self._searcher.search_scholar(query)
        elif search_type == "code":
            results = self._searcher.search_code(query)
        else:
            results = self._searcher.search_scientific(query)
        return results[:max_results]

    def ingest(self, file_path: str | Path):
        """Ingest a document and return created chunks count."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        # Lazy import to prevent OpenCV/libGL requirements during API boot
        from app.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline()
        chunks = pipeline.ingest_document(path)
        vector_store = get_vector_store()
        vector_store.add_texts(chunks)
        return len(chunks)
