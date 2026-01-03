"""Numerical Simulation Agent - Numerical methods and simulations."""

from typing import Optional

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, NUMERICAL_PROMPTS, get_system_prompt
from app.tools.calculator import ScientificCalculator
from app.tools.python_exec import PythonExecutor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NumericalSimulationAgent:
    """Perform numerical simulations and method recommendations."""
    
    def __init__(self):
        """Initialize numerical simulation agent."""
        self.llm = get_llm(temperature=0.2)
        self.calculator = ScientificCalculator()
        self.python_executor = PythonExecutor()
        self.system_prompt = get_system_prompt(AgentRole.NUMERICAL)
    
    def simulate(self, query: str, context: ResearchContext) -> ResearchContext:
        """Perform numerical simulation."""
        logger.info(f"Numerical simulation: {query[:100]}")
        
        # Determine simulation type
        sim_type = self._determine_simulation_type(query)
        
        # Generate simulation prompt
        sim_prompt = f"""{self.system_prompt}

Problem: {query}

Request: {NUMERICAL_PROMPTS.get(sim_type, 'Recommend numerical approach:')}

Please provide:
1. Recommended numerical method(s)
2. Discretization strategy
3. Stability conditions and CFL constraints
4. Expected convergence rate
5. Error estimation
6. Python implementation outline

Be specific and practical."""
        
        try:
            # Get recommendations from LLM
            try:
                ai = self.llm.invoke(sim_prompt)
                recommendations = getattr(ai, "content", str(ai))
            except Exception as e:
                logger.warning(f"LLM numerical invocation failed: {e}")
                recommendations = "Numerical recommendations unavailable from LLM; proceed with stability checks."
                
                # Fallback: Use calculator for numerical analysis
                try:
                    calc_result = self._calculator_assisted_analysis(query, sim_type)
                    if calc_result:
                        recommendations += f"\n\n[CALCULATOR ASSISTED]\n{calc_result}"
                except Exception as calc_e:
                    logger.warning(f"Calculator assisted analysis also failed: {calc_e}")
            
            context.numerical_results["recommendations"] = recommendations
            
            # Try to extract and execute code
            code = self._extract_python_code(recommendations)
            if code:
                execution_result = self.python_executor.execute_code(code)
                context.numerical_results["execution"] = execution_result
                context.numerical_code.append(code)
            
            context.execution_path.append("numerical")
            logger.info(f"Numerical simulation completed")
            
        except Exception as e:
            logger.error(f"Numerical simulation error: {str(e)}")
            context.errors.append(f"Numerical simulation failed: {str(e)}")
        
        return context
    
    def _calculator_assisted_analysis(self, query: str, sim_type: str) -> Optional[str]:
        """Use calculator to assist with numerical analysis when LLM unavailable."""
        try:
            if sim_type == "ode_solver":
                return ("ODE Solver Recommendation: Use Euler method for non-stiff systems. "
                       "Calculator provides euler_stability_analysis() to check stability conditions. "
                       "Use dt << lambda_min for stability (lambda_min = smallest eigenvalue).")
            
            elif sim_type == "optimization":
                return ("Optimization Recommendation: For convex problems (logistic regression), "
                       "use gradient descent via calculator.gradient_descent_visualization(). "
                       "Guaranteed convergence with proper learning rate selection.")
            
            elif sim_type == "convergence":
                return ("Convergence Analysis: Calculator provides convergence_rate_generator() "
                       "and richardson_extrapolation() for quantifying convergence rates. "
                       "Use for mesh refinement studies and error estimation.")
            
            elif sim_type == "error_analysis":
                return ("Error Analysis: Calculate discretization error using richardson_extrapolation() "
                       "to estimate true error from multiple grid refinements. "
                       "Provides posterior error bounds for adaptive methods.")
            
        except Exception as e:
            logger.debug(f"Calculator assisted analysis error: {e}")
            return None
        
        return None
    
    @staticmethod
    def _determine_simulation_type(query: str) -> str:
        """Determine type of simulation needed."""
        query_lower = query.lower()
        
        if "ode" in query_lower:
            return "ode_solver"
        elif "pde" in query_lower:
            return "pde_solver"
        elif "optim" in query_lower:
            return "optimization"
        elif "converg" in query_lower:
            return "convergence"
        elif "error" in query_lower:
            return "error_analysis"
        else:
            return "ode_solver"
    
    @staticmethod
    def _extract_python_code(text: str) -> str:
        """Extract Python code from response."""
        import re
        
        # Look for code blocks
        pattern = r'```python(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        return ""
