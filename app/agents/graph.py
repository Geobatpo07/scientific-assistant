"""LangGraph orchestration for multi-agent workflow."""

from typing import Optional

from app.agents.states import ResearchContext
from app.agents.planner import PlannerAgent
from app.agents.mathematician import MathematicalAnalystAgent
from app.agents.numerical import NumericalSimulationAgent
from app.agents.data_scientist import DataScientistAgent
from app.agents.literature import LiteratureResearchAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.writer import ScientificWriterAgent
from app.agents.memory import MemoryAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TeslasAIOrchestrator:
    """Orchestrate multi-agent research workflow using LangGraph principles."""
    
    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.planner = PlannerAgent()
        self.mathematician = MathematicalAnalystAgent()
        self.numerical = NumericalSimulationAgent()
        self.data_scientist = DataScientistAgent()
        self.literature = LiteratureResearchAgent()
        self.reviewer = ReviewerAgent()
        self.writer = ScientificWriterAgent()
        self.memory = MemoryAgent()
    
    def run_research(self, query: str) -> ResearchContext:
        """Execute complete research workflow."""
        logger.info(f"Starting Teslas.ai research workflow: {query}")
        
        # Initialize context
        context = ResearchContext(main_query=query)
        
        try:
            # Stage 1: Planning
            logger.info("=== STAGE 1: PLANNING ===")
            context = self.planner.plan(query, context)
            
            # Stage 2: Parallel analyses (could be parallelized with LangGraph)
            logger.info("=== STAGE 2: RESEARCH ANALYSES ===")
            
            # Mathematical analysis
            if context.research_plan and "mathematical" in str(context.research_plan.required_analyses):
                context = self.mathematician.analyze(query, context)
            
            # Numerical analysis
            if context.research_plan and "numerical" in str(context.research_plan.required_analyses):
                context = self.numerical.simulate(query, context)
            
            # Data science analysis
            if context.research_plan and "data" in str(context.research_plan.required_analyses):
                context = self.data_scientist.analyze(query, context)
            
            # Literature research
            if context.research_plan and "literature" in str(context.research_plan.required_analyses):
                context = self.literature.research(query, context)
            
            # Stage 3: Review
            logger.info("=== STAGE 3: REVIEW ===")
            context = self.reviewer.review(context)
            
            # Stage 4: Writing
            logger.info("=== STAGE 4: WRITING ===")
            context = self.writer.write(context)
            
            # Stage 5: Memory
            logger.info("=== STAGE 5: MEMORY CURATION ===")
            context = self.memory.curate(context)
            
            logger.info(f"Research completed. Path: {' -> '.join(context.execution_path)}")
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            context.errors.append(f"Workflow error: {str(e)}")
        
        return context
    
    def run_research_selective(
        self,
        query: str,
        agents: Optional[list] = None,
    ) -> ResearchContext:
        """Run research with selected agents only."""
        if agents is None:
            agents = ["planner", "mathematician", "reviewer", "writer"]
        
        logger.info(f"Starting selective research with agents: {agents}")
        
        context = ResearchContext(main_query=query)
        
        try:
            if "planner" in agents:
                context = self.planner.plan(query, context)
            
            if "mathematician" in agents:
                context = self.mathematician.analyze(query, context)
            
            if "numerical" in agents:
                context = self.numerical.simulate(query, context)
            
            if "data_scientist" in agents:
                context = self.data_scientist.analyze(query, context)
            
            if "literature" in agents:
                context = self.literature.research(query, context)
            
            if "reviewer" in agents:
                context = self.reviewer.review(context)
            
            if "writer" in agents:
                context = self.writer.write(context)
            
            if "memory" in agents:
                context = self.memory.curate(context)
            
            logger.info(f"Selective research completed")
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            context.errors.append(f"Workflow error: {str(e)}")
        
        return context


def create_orchestrator() -> TeslasAIOrchestrator:
    """Create orchestrator instance."""
    return TeslasAIOrchestrator()
