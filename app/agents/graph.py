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
from app.config import ExecutionMode, ModeConfig
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
    
    def run_research(self, query: str, mode: ExecutionMode = ExecutionMode.FAST) -> ResearchContext:
        """Execute complete research workflow with specified execution mode.
        
        Parameters
        ----------
        query : str
            Research question or query
        mode : ExecutionMode, optional
            Execution mode (FAST or FULL), defaults to FAST
            - FAST: Quick answers, minimal agents, shorter runtime
            - FULL: Deep research, all agents, maximum rigor
        
        Returns
        -------
        ResearchContext
            Complete research context with results from all executed agents
        """
        logger.info(f"Starting Teslas.ai research workflow: {query} [Mode: {mode.value.upper()}]")
        
        # Get mode configuration
        agent_config = ModeConfig.get_agent_config(mode)
        iteration_config = ModeConfig.get_iteration_config(mode)
        
        # Initialize context with mode metadata
        context = ResearchContext(main_query=query)
        context.metadata["execution_mode"] = mode.value
        context.metadata["agent_config"] = agent_config
        context.metadata["max_iterations"] = iteration_config["max_iterations"]
        
        agent_call_count = 0
        max_agent_calls = iteration_config["max_agent_calls"]
        agent_call_count = 0
        max_agent_calls = iteration_config["max_agent_calls"]
        
        try:
            # Stage 1: Planning
            # FAST: optional (lightweight), FULL: always enabled
            if agent_config["planner"]:
                logger.info("=== STAGE 1: PLANNING ===")
                context = self.planner.plan(query, context)
                agent_call_count += 1
            elif agent_config["planner"] == "optional":
                # In FAST mode, do lightweight planning
                logger.info("=== STAGE 1: LIGHTWEIGHT PLANNING (FAST MODE) ===")
                context = self.planner.plan(query, context)
                agent_call_count += 1
            
            # Stage 2: Parallel analyses
            logger.info(f"=== STAGE 2: RESEARCH ANALYSES (Mode: {mode.value.upper()}) ===")
            
            # Check if we've hit agent call limit
            if agent_call_count >= max_agent_calls:
                logger.warning(f"Agent call limit reached: {agent_call_count}/{max_agent_calls}")
                context.metadata["truncated"] = True
            
            # Mathematical analysis
            # FAST: optional (only if clearly mathematical), FULL: enabled if relevant
            if agent_call_count < max_agent_calls:
                run_math = False
                if agent_config["mathematician"] is True:
                    # FULL mode: run if plan requires it
                    if context.research_plan and "mathematical" in str(context.research_plan.required_analyses):
                        run_math = True
                elif agent_config["mathematician"] == "optional":
                    # FAST mode: run only if explicitly required
                    if context.research_plan and "mathematical" in str(context.research_plan.required_analyses):
                        run_math = True
                
                if run_math:
                    context = self.mathematician.analyze(query, context)
                    agent_call_count += 1
            
            # Numerical analysis
            # FAST: optional (only if clearly numerical), FULL: enabled if relevant
            if agent_call_count < max_agent_calls:
                run_numerical = False
                if agent_config["numerical"] is True:
                    # FULL mode: run if plan requires it
                    if context.research_plan and "numerical" in str(context.research_plan.required_analyses):
                        run_numerical = True
                elif agent_config["numerical"] == "optional":
                    # FAST mode: run only if explicitly required
                    if context.research_plan and "numerical" in str(context.research_plan.required_analyses):
                        run_numerical = True
                
                if run_numerical:
                    context = self.numerical.simulate(query, context)
                    agent_call_count += 1
            
            # Data science analysis
            # FAST: disabled, FULL: enabled if relevant
            if agent_call_count < max_agent_calls:
                if agent_config["data_scientist"] is True:
                    if context.research_plan and "data" in str(context.research_plan.required_analyses):
                        context = self.data_scientist.analyze(query, context)
                        agent_call_count += 1
            
            # Literature research
            # FAST: optional (quick search), FULL: comprehensive
            if agent_call_count < max_agent_calls:
                run_literature = False
                if agent_config["literature"] is True:
                    # FULL mode: run if plan requires it
                    if context.research_plan and "literature" in str(context.research_plan.required_analyses):
                        run_literature = True
                elif agent_config["literature"] == "optional":
                    # FAST mode: quick search only
                    if context.research_plan and "literature" in str(context.research_plan.required_analyses):
                        run_literature = True
                
                if run_literature:
                    context = self.literature.research(query, context)
                    agent_call_count += 1
            
            # Stage 3: Review
            # FAST: disabled (no deep review), FULL: enabled
            if agent_call_count < max_agent_calls:
                if agent_config["reviewer"] is True:
                    logger.info("=== STAGE 3: SCIENTIFIC REVIEW ===")
                    context = self.reviewer.review(context)
                    agent_call_count += 1
                else:
                    logger.info("=== STAGE 3: REVIEW SKIPPED (FAST MODE) ===")
            
            # Stage 4: Writing
            # FAST: concise output, FULL: detailed output
            if agent_call_count < max_agent_calls:
                if agent_config["writer"]:
                    logger.info(f"=== STAGE 4: WRITING ({mode.value.upper()} MODE) ===")
                    # Writer should be aware of mode for output formatting
                    context.metadata["writer_mode"] = mode.value
                    context = self.writer.write(context)
                    agent_call_count += 1
            
            # Stage 5: Memory
            # FAST: disabled (no memory curation), FULL: enabled
            if agent_call_count < max_agent_calls:
                if agent_config["memory"] is True:
                    logger.info("=== STAGE 5: MEMORY CURATION ===")
                    context = self.memory.curate(context)
                    agent_call_count += 1
                else:
                    logger.info("=== STAGE 5: MEMORY CURATION SKIPPED (FAST MODE) ===")
            
            # Record execution metadata
            context.metadata["agent_calls"] = agent_call_count
            context.metadata["execution_complete"] = agent_call_count < max_agent_calls
            
            logger.info(
                f"Research completed. Mode: {mode.value.upper()}, "
                f"Agents: {agent_call_count}, Path: {' -> '.join(context.execution_path)}"
            )
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            context.errors.append(f"Workflow error: {str(e)}")
        
        return context
    
    def run_research_selective(
        self,
        query: str,
        agents: Optional[list] = None,
        mode: ExecutionMode = ExecutionMode.FAST,
    ) -> ResearchContext:
        """Run research with selected agents and execution mode.
        
        Parameters
        ----------
        query : str
            Research question
        agents : list, optional
            List of agent names to execute. If None, uses default set.
        mode : ExecutionMode, optional
            Execution mode for parameter configuration (FAST or FULL)
        
        Returns
        -------
        ResearchContext
            Research context with results from selected agents
        """
        if agents is None:
            agents = ["planner", "mathematician", "reviewer", "writer"]
        
        logger.info(f"Starting selective research with agents: {agents} [Mode: {mode.value.upper()}]")
        
        # Get mode configuration for metadata
        iteration_config = ModeConfig.get_iteration_config(mode)
        
        context = ResearchContext(main_query=query)
        context.metadata["execution_mode"] = mode.value
        context.metadata["selective_agents"] = agents
        context.metadata["max_iterations"] = iteration_config["max_iterations"]
        
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
