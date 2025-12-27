"""Data Scientist Agent - Data analysis and ML."""

from typing import Optional

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, DATA_SCIENCE_PROMPTS, get_system_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DataScientistAgent:
    """Perform data science analysis."""
    
    def __init__(self):
        """Initialize data scientist agent."""
        self.llm = get_llm(temperature=0.3)
        self.system_prompt = get_system_prompt(AgentRole.DATA_SCIENTIST)
    
    def analyze(self, query: str, context: ResearchContext) -> ResearchContext:
        """Perform data science analysis."""
        logger.info(f"Data science analysis: {query[:100]}")
        
        # Determine analysis type
        analysis_type = self._determine_analysis_type(query)
        
        # Generate analysis prompt
        analysis_prompt = f"""{self.system_prompt}

Problem: {query}

Request: {DATA_SCIENCE_PROMPTS.get(analysis_type, 'Analyze the data scientifically:')}

Please provide:
1. Data exploration insights
2. Statistical findings
3. Model recommendations
4. Validation strategy
5. Uncertainty quantification
6. Interpretation and limitations

Be thorough and scientifically rigorous."""
        
        try:
            # Get analysis from LLM
            try:
                ai = self.llm.invoke(analysis_prompt)
                analysis_text = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM data scientist invocation failed: {e}")
                analysis_text = "Data science analysis unavailable from LLM; use validators and metrics heuristics."
            context.data_analysis["insights"] = analysis_text
            
            # Extract findings
            findings = self._extract_findings(analysis_text)
            context.statistical_findings.extend(findings)
            
            context.execution_path.append("data_scientist")
            logger.info(f"Data science analysis completed")
            
        except Exception as e:
            logger.error(f"Data science analysis error: {str(e)}")
            context.errors.append(f"Data science analysis failed: {str(e)}")
        
        return context
    
    @staticmethod
    def _determine_analysis_type(query: str) -> str:
        """Determine type of data analysis."""
        query_lower = query.lower()
        
        if "explore" in query_lower or "eda" in query_lower:
            return "eda"
        elif "model" in query_lower or "machine learning" in query_lower:
            return "model_selection"
        elif "hypothes" in query_lower or "test" in query_lower:
            return "hypothesis_test"
        elif "time" in query_lower or "forecast" in query_lower:
            return "time_series"
        elif "uncertain" in query_lower:
            return "uncertainty"
        else:
            return "eda"
    
    @staticmethod
    def _extract_findings(text: str) -> list:
        """Extract key findings from analysis."""
        findings = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                # Heuristic: extract sentences with insights
                if any(keyword in line.lower() for keyword in 
                       ["finding", "result", "show", "indicate", "suggest", "recommend"]):
                    findings.append(line)
        
        return findings[:10]
