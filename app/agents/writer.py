"""Scientific Writer Agent - Academic content generation."""

from typing import Optional

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, get_system_prompt
from app.tools.latex import LaTeXGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScientificWriterAgent:
    """Write publication-quality scientific content."""
    
    def __init__(self):
        """Initialize scientific writer."""
        self.llm = get_llm(temperature=0.3)
        self.latex_gen = LaTeXGenerator()
        self.system_prompt = get_system_prompt(AgentRole.WRITER)
    
    def write(self, context: ResearchContext) -> ResearchContext:
        """Write final scientific report."""
        logger.info("Writing scientific report...")
        
        try:
            # Compile research for writing
            research_data = self._compile_research_data(context)
            
            # Generate writing prompt
            writing_prompt = f"""{self.system_prompt}

Research Data:
{research_data}

Please write a comprehensive scientific report including:
1. Abstract (150-200 words)
2. Introduction
3. Methodology
4. Results
5. Discussion
6. Conclusion
7. Properly formatted references

Use LaTeX for equations. Maintain academic tone throughout.
Include specific results and interpretations from the research."""
            
            # Get written report
            try:
                ai = self.llm.invoke(writing_prompt)
                report = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM writer invocation failed: {e}")
                report = "Scientific report unavailable from LLM; compile from validated findings."

            # Strip any full LaTeX preamble the model may have produced to avoid double \documentclass
            report_clean = self._strip_latex_preamble(report)
            context.final_summary = report_clean

            # Try to convert to LaTeX document
            latex_doc = self.latex_gen.create_document(
                title=context.main_query,
                content=report_clean,
            )
            context.metadata["latex_document"] = latex_doc
            
            context.execution_path.append("writer")
            logger.info("Scientific report completed")
            
        except Exception as e:
            logger.error(f"Writing error: {str(e)}")
            context.errors.append(f"Writing failed: {str(e)}")
        
        return context
    
    @staticmethod
    def _compile_research_data(context: ResearchContext) -> str:
        """Compile research data for writing."""
        data = f"""Original Question: {context.main_query}

Mathematical Insights:
{chr(10).join(context.mathematical_insights[:3])}

Numerical Results:
{str(list(context.numerical_results.items())[:3])}

Data Analysis Findings:
{chr(10).join(context.statistical_findings[:3])}

Literature Review:
- Found {len(context.literature_sources)} relevant sources
Bibliography: {context.bibliography[:500]}...

Critical Review:
- Criticisms: {chr(10).join(context.criticisms[:3])}
- Improvements: {chr(10).join(context.improvements[:3])}

Key Equations:
{chr(10).join(context.final_equations[:5])}
"""
        return data

    @staticmethod
    def _strip_latex_preamble(text: str) -> str:
        """Remove model-generated LaTeX preamble if present to avoid double wrapping."""
        if "\\documentclass" not in text:
            return text
        start = text.find("\\begin{document}")
        end = text.rfind("\\end{document}")
        if start == -1:
            return text
        body = text[start + len("\\begin{document}") : end if end != -1 else None]
        return body.strip()
