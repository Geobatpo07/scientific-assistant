"""API request and response schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.config import ExecutionMode


class ResearchRequest(BaseModel):
    """Request for scientific research."""
    
    query: str = Field(..., description="Research question or query")
    agents: Optional[List[str]] = Field(
        default=None,
        description="List of agents to use (planner, mathematician, numerical, data_scientist, literature, reviewer, writer, memory)"
    )
    mode: ExecutionMode = Field(
        default=ExecutionMode.FAST,
        description="Execution mode: 'fast' for quick answers (minimal latency, reduced agents), 'full' for deep research (maximum rigor, all agents)"
    )
    stream: bool = Field(default=False, description="Stream results")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AgentResult(BaseModel):
    """Result from an agent."""
    
    agent: str
    success: bool
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchResponse(BaseModel):
    """Response with research results."""
    
    query: str
    mode: str = Field(default="fast", description="Execution mode used (fast or full)")
    status: str = Field(default="completed")
    summary: str
    mathematical_insights: List[str] = Field(default_factory=list)
    numerical_results: Dict[str, Any] = Field(default_factory=dict)
    data_analysis: Dict[str, Any] = Field(default_factory=dict)
    literature_sources: List[Dict[str, str]] = Field(default_factory=list)
    criticisms: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    final_equations: List[str] = Field(default_factory=list)
    execution_path: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    latex_document: Optional[str] = None


class SearchRequest(BaseModel):
    """Request for web search."""
    
    query: str
    search_type: str = Field(default="scientific")  # scientific, arxiv, scholar, code
    max_results: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    """Search result."""
    
    title: str
    url: str
    summary: str
    source: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    timestamp: str
