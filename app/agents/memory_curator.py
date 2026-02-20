"""Memory Curator Agent - Knowledge management."""

from typing import Optional

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, get_system_prompt
from app.vectorstore.store import get_vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryCuratorAgent:
    """Curate and organize research memory."""
    
    def __init__(self):
        """Initialize memory curator."""
        self.llm = get_llm(temperature=0.2)
        self.vector_store = get_vector_store()
        self.system_prompt = get_system_prompt(AgentRole.MEMORY)
    
    def curate(self, context: ResearchContext) -> ResearchContext:
        """Curate research memory."""
        logger.info("Curating research memory...")
        
        try:
            # Extract key findings
            key_findings = self._extract_key_findings(context)
            
            # Generate summary for memory
            summary_prompt = f"""{self.system_prompt}

Research Query: {context.main_query}

Key Findings:
{chr(10).join(key_findings[:10])}

Execution Summary:
- Agents executed: {', '.join(context.execution_path)}
- Errors: {len(context.errors)}
- Insights: {len(context.mathematical_insights) + len(context.statistical_findings)}

Please create a concise research summary suitable for memory storage."""
            
            try:
                ai = self.llm.invoke(summary_prompt)
                memory_summary = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM memory curator invocation failed: {e}")
                memory_summary = "Memory summary unavailable from LLM; persist validated highlights and citations."
            
            # Store in vector store
            self._store_in_memory(
                query=context.main_query,
                summary=memory_summary,
                findings=key_findings,
            )
            
            context.metadata["memory_stored"] = True
            context.execution_path.append("memory_curator")
            
            logger.info("Research memory curated and stored")
            
        except Exception as e:
            logger.error(f"Memory curation error: {str(e)}")
            context.errors.append(f"Memory curation failed: {str(e)}")
        
        return context
    
    @staticmethod
    def _extract_key_findings(context: ResearchContext) -> list:
        """Extract key findings from all agents."""
        findings = []
        
        # Mathematical findings
        findings.extend(context.mathematical_insights[:3])
        
        # Statistical findings
        findings.extend(context.statistical_findings[:3])
        
        # Improvements from review
        findings.extend(context.improvements[:3])
        
        return [f for f in findings if f]
    
    def _store_in_memory(self, query: str, summary: str, findings: list) -> None:
        """Store research in vector store."""
        try:
            text_to_store = f"Query: {query}\n\nSummary: {summary}\n\nKey Findings:\n" + "\n".join(findings)
            
            self.vector_store.add_texts(
                texts=[text_to_store],
                metadatas=[{
                    "type": "research_memory",
                    "query": query,
                    "timestamp": str(__import__("datetime").datetime.now()),
                }],
            )
            
            logger.info("Research stored in memory")
        except Exception as e:
            logger.error(f"Error storing in memory: {str(e)}")
