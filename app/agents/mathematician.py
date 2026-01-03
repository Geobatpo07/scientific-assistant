"""Mathematical Analyst Agent - Rigorous mathematical analysis."""

from typing import Optional

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, MATHEMATICAL_PROMPTS, get_system_prompt
from app.tools.calculator import ScientificCalculator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MathematicalAnalystAgent:
    """Perform rigorous mathematical analysis."""
    
    def __init__(self):
        """Initialize mathematical analyst."""
        self.llm = get_llm(temperature=0.1)  # Very low temperature
        self.calculator = ScientificCalculator()
        self.system_prompt = get_system_prompt(AgentRole.MATHEMATICIAN)
    
    def analyze(self, query: str, context: ResearchContext) -> ResearchContext:
        """Perform mathematical analysis."""
        logger.info(f"Mathematical analysis: {query[:100]}")
        
        # Determine analysis type
        analysis_type = self._determine_analysis_type(query)
        
        # Generate analysis prompt
        analysis_prompt = f"""{self.system_prompt}

Problem: {query}

Request: {MATHEMATICAL_PROMPTS.get(analysis_type, 'Analyze the following mathematically:')}

Please provide:
1. Mathematical formulation
2. Key theorems and principles
3. Derivations and proofs
4. Physical/intuitive interpretation
5. Limitations and assumptions

Be rigorous and explicit in all steps."""
        
        try:
            # Get analysis from LLM
            try:
                ai = self.llm.invoke(analysis_prompt)
                analysis_text = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM mathematician invocation failed: {e}")
                analysis_text = "Mathematical analysis unavailable from LLM; rely on symbolic and numeric validators."
                
                # Fallback: Use calculator for symbolic analysis
                try:
                    calc_result = self._calculator_assisted_analysis(query, analysis_type)
                    if calc_result:
                        analysis_text += f"\n\n[CALCULATOR ASSISTED]\n{calc_result}"
                except Exception as calc_e:
                    logger.warning(f"Calculator assisted analysis also failed: {calc_e}")
            
            context.mathematical_insights.append(analysis_text)
            
            # Try to extract equations
            equations = self._extract_equations(analysis_text)
            context.final_equations.extend(equations)
            
            context.execution_path.append("mathematician")
            logger.info(f"Mathematical analysis completed")
            
        except Exception as e:
            logger.error(f"Mathematical analysis error: {str(e)}")
            context.errors.append(f"Mathematical analysis failed: {str(e)}")
        
        return context
    
    def _calculator_assisted_analysis(self, query: str, analysis_type: str) -> Optional[str]:
        """Use calculator to assist with mathematical analysis when LLM unavailable."""
        try:
            # Try to extract mathematical expression from query
            import re
            expr_pattern = r'(?:of|for)\s+([x\w\d\^*+\-/().\s]+)(?:\s|$)'
            matches = re.findall(expr_pattern, query, re.IGNORECASE)
            
            if not matches:
                return None
            
            expr = matches[0].strip()
            
            if analysis_type == "differentiation":
                result = self.calculator.symbolic.differentiate(expr, "x")
                if result.success:
                    return f"Derivative: d/dx[{expr}] = {result.results.get('simplified', 'N/A')}"
            
            elif analysis_type == "integration":
                result = self.calculator.symbolic.integrate(expr, "x")
                if result.success:
                    return f"Integral: ∫{expr}dx = {result.results.get('simplified', 'N/A')}"
            
            elif analysis_type == "series":
                result = self.calculator.symbolic.taylor_series(expr, "x", 0, 3)
                if result.success:
                    return f"Series: {result.results.get('series', 'N/A')}"
            
        except Exception as e:
            logger.debug(f"Calculator assisted analysis error: {e}")
            return None
        
        return None
    
    @staticmethod
    def _determine_analysis_type(query: str) -> str:
        """Determine type of mathematical analysis needed."""
        query_lower = query.lower()
        
        if "deriv" in query_lower:
            return "differentiation"
        elif "integr" in query_lower:
            return "integration"
        elif "lim" in query_lower:
            return "limit"
        elif "series" in query_lower or "taylor" in query_lower:
            return "series"
        elif "solve" in query_lower or "equation" in query_lower:
            return "solve_equation"
        elif "stabil" in query_lower:
            return "stability"
        else:
            return "differentiation"
    
    @staticmethod
    def _extract_equations(text: str) -> list:
        """Extract equations from analysis text."""
        import re
        
        # Look for LaTeX equations
        equation_pattern = r'\$\$(.*?)\$\$'
        equations = re.findall(equation_pattern, text, re.DOTALL)
        
        return equations[:10]  # Limit to 10 equations
