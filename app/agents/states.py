"""Agent state definitions for LangGraph."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ResearchPlan:
    """Structured research plan."""
    
    main_question: str
    decomposed_tasks: List[str] = field(default_factory=list)
    required_analyses: List[str] = field(default_factory=list)
    agent_assignments: Dict[str, str] = field(default_factory=dict)
    estimated_complexity: str = "unknown"
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ResearchContext:
    """Shared context across all agents."""
    
    # Main research question
    main_query: str
    
    # Planning
    research_plan: Optional[ResearchPlan] = None
    
    # Mathematical analysis
    mathematical_insights: List[str] = field(default_factory=list)
    mathematical_proofs: Dict[str, str] = field(default_factory=dict)
    
    # Numerical results
    numerical_results: Dict[str, Any] = field(default_factory=dict)
    numerical_code: List[str] = field(default_factory=list)
    
    # Data science results
    data_analysis: Dict[str, Any] = field(default_factory=dict)
    statistical_findings: List[str] = field(default_factory=list)
    
    # Literature
    literature_sources: List[Dict[str, str]] = field(default_factory=list)
    relevant_papers: List[str] = field(default_factory=list)
    bibliography: str = ""
    
    # Critical review
    criticisms: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    # Final output
    final_summary: str = ""
    final_equations: List[str] = field(default_factory=list)
    final_references: List[str] = field(default_factory=list)
    
    # Metadata
    execution_path: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Message from an agent."""
    
    agent: str
    action: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
