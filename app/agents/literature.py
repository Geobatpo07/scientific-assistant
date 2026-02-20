"""Literature Research Agent - Document search and synthesis."""

from typing import Optional

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, get_system_prompt
from app.rag.chains import create_rag_chain
from app.tools.duckduckgo_search import create_searcher
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LiteratureResearchAgent:
    """Research literature using RAG and web search."""
    
    def __init__(self):
        """Initialize literature research agent."""
        self.llm = get_llm(temperature=0.2)
        self.rag_chain = create_rag_chain()
        self.searcher = create_searcher()
        self.system_prompt = get_system_prompt(AgentRole.LITERATURE)
    
    def research(self, query: str, context: ResearchContext) -> ResearchContext:
        """Search literature and synthesize findings."""
        logger.info(f"Literature research: {query[:100]}")
        
        try:
            # Search internal knowledge base (RAG)
            logger.info("Searching internal knowledge base...")
            rag_results = self.rag_chain.retrieve_and_generate(query, k=5)
            
            # Search web
            logger.info("Searching web sources...")
            web_results = self.searcher.search_scientific(query)
            
            # Synthesize
            synthesis_prompt = f"""{self.system_prompt}

Research Topic: {query}

Internal Documents:
{rag_results['context']}

Web Results:
{self._format_web_results(web_results)}

Please synthesize these sources and provide:
1. Key concepts and definitions
2. Current state of research
3. Recent breakthroughs
4. Relevant methodologies
5. Research gaps
6. Comprehensive bibliography (APA format)

Ensure proper citations throughout."""
            
            try:
                ai = self.llm.invoke(synthesis_prompt)
                synthesis = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM literature invocation failed: {e}")
                synthesis = "Literature synthesis unavailable from LLM; rely on sourced abstracts and summaries."
            context.literature_sources.extend(web_results)
            context.bibliography = synthesis
            
            context.execution_path.append("literature")
            logger.info(f"Literature research completed")
            
        except Exception as e:
            logger.error(f"Literature research error: {str(e)}")
            context.errors.append(f"Literature research failed: {str(e)}")
        
        return context
    
    @staticmethod
    def _format_web_results(results: list) -> str:
        """Format web search results."""
        formatted = ""
        for i, result in enumerate(results, 1):
            formatted += f"""{i}. Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Summary: {result.get('summary', 'N/A')}

"""
        return formatted
