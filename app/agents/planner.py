"""Planner Agent - Decomposes research questions into actionable tasks."""

from typing import Optional

from app.agents.states import ResearchContext, ResearchPlan
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, get_system_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    """Plan research approach by decomposing questions."""
    
    def __init__(self):
        """Initialize planner agent."""
        self.llm = get_llm(temperature=0.2)  # Lower temperature for planning
        self.system_prompt = get_system_prompt(AgentRole.PLANNER)
    
    def plan(self, query: str, context: Optional[ResearchContext] = None) -> ResearchContext:
        """Create research plan for given query."""
        logger.info(f"Planning research approach for: {query[:100]}")
        
        if context is None:
            context = ResearchContext(main_query=query)
        else:
            context.main_query = query
        
        # Generate planning prompt
        planning_prompt = f"""{self.system_prompt}

Research Question: {query}

Please provide:
1. Decomposed tasks (list of sub-problems)
2. Required analyses (mathematical, numerical, data-driven, literature)
3. Agent assignments (which agent for which task)
4. Estimated computational complexity
5. Dependencies between tasks

Structure your response clearly with sections."""
        
        # Get plan from LLM
        try:
            try:
                ai = self.llm.invoke(planning_prompt)
                plan_text = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM planning invocation failed: {e}")
                plan_text = "Plan unavailable from LLM; use heuristic steps and validators."
            
            # Parse plan (simplified - in production use structured output)
            research_plan = ResearchPlan(
                main_question=query,
                decomposed_tasks=self._extract_tasks(plan_text),
                required_analyses=self._extract_analyses(plan_text),
                agent_assignments=self._extract_assignments(plan_text),
            )
            
            context.research_plan = research_plan
            context.execution_path.append("planner")
            
            logger.info(f"Created plan with {len(research_plan.decomposed_tasks)} tasks")
            
        except Exception as e:
            logger.error(f"Planning error: {str(e)}")
            context.errors.append(f"Planning failed: {str(e)}")
        
        return context
    
    @staticmethod
    def _extract_tasks(text: str) -> list:
        """Extract task list from planning text."""
        tasks = []
        lines = text.split('\n')
        
        in_tasks_section = False
        for line in lines:
            if 'task' in line.lower() and ('1.' in line or 'decomposed' in line.lower()):
                in_tasks_section = True
            elif in_tasks_section:
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                    task = line.strip().lstrip('0123456789.- ')
                    if task and len(task) > 5:
                        tasks.append(task)
                elif line.strip() == "":
                    in_tasks_section = False
        
        return tasks[:10]  # Limit to 10 tasks
    
    @staticmethod
    def _extract_analyses(text: str) -> list:
        """Extract required analyses."""
        analyses = []
        keywords = ["mathematical", "numerical", "data", "literature", "statistical"]
        
        for keyword in keywords:
            if keyword in text.lower():
                analyses.append(keyword.capitalize())
        
        return analyses
    
    @staticmethod
    def _extract_assignments(text: str) -> dict:
        """Extract agent assignments."""
        assignments = {}
        agent_keywords = {
            "mathematician": "mathematical",
            "numerical": "numerical",
            "data_scientist": "data",
            "literature": "literature",
        }
        
        for agent, keyword in agent_keywords.items():
            if keyword in text.lower():
                assignments[agent] = keyword
        
        return assignments
