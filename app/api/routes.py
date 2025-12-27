"""FastAPI routes for Teslas.ai assistant."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.assistant import Assistant
from app.api.schemas import (
    ResearchRequest,
    ResearchResponse,
    SearchRequest,
    SearchResult,
    HealthResponse,
)
from app.vectorstore.store import get_vector_store
from app.llm.ollama import get_llm
from app.tools.duckduckgo_search import create_searcher
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Single facade (lazy to avoid blocking startup while LLM loads)
assistant: Optional[Assistant] = None


def get_assistant() -> Assistant:
    """Return singleton Assistant, creating it on first use."""
    global assistant
    if assistant is None:
        logger.info("Creating Assistant singleton")
        assistant = Assistant()
    return assistant


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.2.0",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Execute scientific research."""
    logger.info(f"Research request: {request.query}")
    
    try:
        # Run research
        context = get_assistant().research(request.query, request.agents)
        
        # Format response
        latex_doc = context.metadata.get("latex_document")
        
        return ResearchResponse(
            query=context.main_query,
            status="completed" if not context.errors else "completed_with_errors",
            summary=context.final_summary,
            mathematical_insights=context.mathematical_insights,
            numerical_results=context.numerical_results,
            data_analysis=context.data_analysis,
            literature_sources=context.literature_sources,
            criticisms=context.criticisms,
            improvements=context.improvements,
            final_equations=context.final_equations,
            execution_path=context.execution_path,
            errors=context.errors,
            latex_document=latex_doc,
        )
        
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search(request: SearchRequest):
    """Search web for scientific content."""
    logger.info(f"Search request: {request.query}")
    
    try:
        results = get_assistant().search(request.query, request.search_type, request.max_results)
        
        return {
            "query": request.query,
            "results": [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    summary=r.get("summary", ""),
                )
                for r in results[:request.max_results]
            ]
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """List available agents."""
    return {
        "agents": [
            "planner",
            "mathematician",
            "numerical",
            "data_scientist",
            "literature",
            "reviewer",
            "writer",
            "memory",
        ],
        "description": "Teslas.ai multi-agent scientific assistant",
    }


@router.get("/kb/count")
async def kb_count():
    """Return knowledge base document count (ChromaDB)."""
    vs = get_vector_store()
    return {"count": vs.count()}


@router.post("/kb/search")
async def kb_search(query: str, k: int = 5):
    """Search hybrid vector store (FAISS + Chroma)."""
    vs = get_vector_store()
    results = vs.search(query=query, k=k)
    return {
        "query": query,
        "results": results,
        "count": len(results),
    }


@router.get("/llm/health")
async def llm_health():
    """Check LLM connectivity via ChatOllama (no direct HTTP)."""
    try:
        llm = get_llm()
        # Best-effort lightweight invoke to confirm pipeline works
        try:
            ai = llm.invoke("ping")
            content = getattr(ai, "content", "")
            return {"status": "ok", "response_preview": content[:80]}
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/ingest")
async def ingest_document(file_path: str):
    """Ingest document into knowledge base."""
    logger.info(f"Ingesting document: {file_path}")
    try:
        count = get_assistant().ingest(file_path)
        return {"status": "success", "file": file_path, "chunks_created": count}
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
