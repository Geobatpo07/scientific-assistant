"""Mathematical analysis tools for calculus, optimization, and linear algebra."""

import numpy as np
from scipy import optimize, linalg
import sympy as sp


class MathematicalAnalysis:
    """
    Tools for mathematical analysis including:
    - Symbolic and numerical differentiation/integration
    - Optimization problems
    - Linear algebra operations
    - Series expansions
    """
    
    def __init__(self):
        """Initialize mathematical analysis tools."""
        pass
    
    def differentiate(self, expression, variable):
        """
        Compute the derivative of a symbolic expression.
        
        Args:
            expression (str or sympy.Expr): The expression to differentiate
            variable (str): The variable to differentiate with respect to
            
        Returns:
            sympy.Expr: The derivative
            
        Example:
            >>> ma = MathematicalAnalysis()
            >>> ma.differentiate("x**2 + 3*x + 2", "x")
            2*x + 3
        """
        if isinstance(expression, str):
            expr = sp.sympify(expression)
        else:
            expr = expression
        
        var = sp.Symbol(variable)
        return sp.diff(expr, var)
    
    def integrate(self, expression, variable, limits=None):
        """
        Compute the integral of a symbolic expression.
        
        Args:
            expression (str or sympy.Expr): The expression to integrate
            variable (str): The variable to integrate with respect to
            limits (tuple, optional): Integration limits (a, b) for definite integral
            
        Returns:
            sympy.Expr or float: The integral result
            
        Example:
            >>> ma = MathematicalAnalysis()
            >>> ma.integrate("x**2", "x")
            x**3/3
            >>> ma.integrate("x**2", "x", (0, 1))
            1/3
        """
        if isinstance(expression, str):
            expr = sp.sympify(expression)
        else:
            expr = expression
        
        var = sp.Symbol(variable)
        
        if limits:
            return sp.integrate(expr, (var, limits[0], limits[1]))
        return sp.integrate(expr, var)
    
    def optimize_function(self, func, x0, method='BFGS', bounds=None):
        """
        Optimize a function using numerical methods.
        
        Args:
            func (callable): Function to minimize
            x0 (array-like): Initial guess
            method (str): Optimization method
            bounds (list of tuples, optional): Bounds for each variable
            
        Returns:
            scipy.optimize.OptimizeResult: Optimization result
            
        Example:
            >>> ma = MathematicalAnalysis()
            >>> result = ma.optimize_function(lambda x: (x[0]-1)**2 + (x[1]-2)**2, [0, 0])
            >>> print(result.x)  # [1., 2.]
        """
        if bounds:
            return optimize.minimize(func, x0, method=method, bounds=bounds)
        return optimize.minimize(func, x0, method=method)
    
    def solve_linear_system(self, A, b):
        """
        Solve a linear system Ax = b.
        
        Args:
            A (array-like): Coefficient matrix
            b (array-like): Right-hand side vector
            
        Returns:
            numpy.ndarray: Solution vector
            
        Example:
            >>> ma = MathematicalAnalysis()
            >>> A = [[2, 1], [1, 3]]
            >>> b = [5, 7]
            >>> x = ma.solve_linear_system(A, b)
            >>> print(x)  # [1., 2.]
        """
        A = np.array(A)
        b = np.array(b)
        return linalg.solve(A, b)
    
    def eigenvalues(self, matrix):
        """
        Compute eigenvalues and eigenvectors of a matrix.
        
        Args:
            matrix (array-like): Input matrix
            
        Returns:
            tuple: (eigenvalues, eigenvectors)
            
        Example:
            >>> ma = MathematicalAnalysis()
            >>> matrix = [[1, 2], [2, 1]]
            >>> vals, vecs = ma.eigenvalues(matrix)
        """
        matrix = np.array(matrix)
        return linalg.eig(matrix)
    
    def taylor_series(self, expression, variable, point=0, order=5):
        """
        Compute Taylor series expansion of an expression.
        
        Args:
            expression (str or sympy.Expr): Expression to expand
            variable (str): Variable for expansion
            point (float): Point around which to expand
            order (int): Order of the expansion
            
        Returns:
            sympy.Expr: Taylor series expansion
            
        Example:
            >>> ma = MathematicalAnalysis()
            >>> ma.taylor_series("sin(x)", "x", 0, 5)
        """
        if isinstance(expression, str):
            expr = sp.sympify(expression)
        else:
            expr = expression
        
        var = sp.Symbol(variable)
        return expr.series(var, point, order).removeO()
