"""Main Scientific Assistant class."""

from .analysis import MathematicalAnalysis
from .numerical import NumericalExperimentation
from .modeling import ModelingTools
from .data_science import DataScienceTools


class ScientificAssistant:
    """
    A high-level scientific assistant for applied mathematics and data science.
    
    This class provides integrated access to various scientific computing tools:
    - Mathematical analysis (calculus, optimization, linear algebra)
    - Numerical experimentation (simulations, numerical methods)
    - Modeling (statistical models, ML models)
    - Data science (data processing, visualization, analysis)
    
    Example:
        >>> assistant = ScientificAssistant()
        >>> result = assistant.analysis.differentiate("x**2 + 3*x + 2", "x")
        >>> print(result)  # 2*x + 3
    """
    
    def __init__(self):
        """Initialize the scientific assistant with all modules."""
        self.analysis = MathematicalAnalysis()
        self.numerical = NumericalExperimentation()
        self.modeling = ModelingTools()
        self.data = DataScienceTools()
    
    def info(self):
        """Display information about available capabilities."""
        info_text = """
Scientific Assistant v0.1.0
==========================

Available modules:
- analysis: Mathematical analysis tools (calculus, optimization, linear algebra)
- numerical: Numerical experimentation tools (simulations, numerical methods)
- modeling: Statistical and ML modeling tools
- data: Data science tools (processing, visualization, analysis)

Example usage:
    >>> assistant = ScientificAssistant()
    >>> assistant.analysis.differentiate("x**2", "x")
    >>> assistant.numerical.solve_ode(...)
    >>> assistant.modeling.linear_regression(X, y)
    >>> assistant.data.load_and_explore(dataframe)
"""
        print(info_text)
        return info_text
