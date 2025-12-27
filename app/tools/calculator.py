"""Scientific calculation tools."""

import sympy as sp
import numpy as np
from typing import Optional, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScientificCalculator:
    """Scientific computing tools."""
    
    @staticmethod
    def differentiate(expr_str: str, var_str: str = "x") -> str:
        """Compute symbolic derivative."""
        try:
            expr = sp.sympify(expr_str)
            var = sp.Symbol(var_str)
            result = sp.diff(expr, var)
            return str(result)
        except Exception as e:
            logger.error(f"Differentiation error: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def integrate(expr_str: str, var_str: str = "x") -> str:
        """Compute symbolic indefinite integral."""
        try:
            expr = sp.sympify(expr_str)
            var = sp.Symbol(var_str)
            result = sp.integrate(expr, var)
            return str(result)
        except Exception as e:
            logger.error(f"Integration error: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def expand_series(expr_str: str, var_str: str = "x", point: int = 0, n: int = 5) -> str:
        """Expand expression as Taylor series."""
        try:
            expr = sp.sympify(expr_str)
            var = sp.Symbol(var_str)
            result = sp.series(expr, var, point, n)
            return str(result)
        except Exception as e:
            logger.error(f"Series expansion error: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def solve(expr_str: str, var_str: str = "x") -> str:
        """Solve equation for variable."""
        try:
            expr = sp.sympify(expr_str)
            var = sp.Symbol(var_str)
            result = sp.solve(expr, var)
            return str(result)
        except Exception as e:
            logger.error(f"Solve error: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def evaluate(expr_str: str, **kwargs) -> Any:
        """Evaluate expression numerically."""
        try:
            expr = sp.sympify(expr_str)
            # Substitute values
            for var, val in kwargs.items():
                expr = expr.subs(sp.Symbol(var), val)
            result = float(expr)
            return result
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}")
            return None


class NumericalTools:
    """Numerical computation tools."""
    
    @staticmethod
    def matrix_operations(operation: str, matrix_data: list) -> Any:
        """Perform matrix operations."""
        try:
            matrix = np.array(matrix_data)
            
            if operation == "determinant":
                return float(np.linalg.det(matrix))
            elif operation == "inverse":
                return np.linalg.inv(matrix).tolist()
            elif operation == "eigenvalues":
                eigenvalues = np.linalg.eigvals(matrix)
                return eigenvalues.tolist()
            elif operation == "rank":
                return int(np.linalg.matrix_rank(matrix))
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"Matrix operation error: {str(e)}")
            return None
    
    @staticmethod
    def linear_regression(x_data: list, y_data: list) -> dict:
        """Perform linear regression."""
        try:
            X = np.array(x_data).reshape(-1, 1)
            y = np.array(y_data)
            
            # Compute coefficients
            A = np.vstack([X.flatten(), np.ones(len(X))]).T
            coeffs = np.linalg.lstsq(A, y, rcond=None)[0]
            
            return {
                "slope": float(coeffs[0]),
                "intercept": float(coeffs[1]),
                "equation": f"y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}",
            }
        except Exception as e:
            logger.error(f"Linear regression error: {str(e)}")
            return None
