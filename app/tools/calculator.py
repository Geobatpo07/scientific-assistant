"""Research-grade scientific computation module for Teslas.ai.

This module provides a comprehensive, structured, and agent-friendly interface
for symbolic mathematics, numerical analysis, linear algebra, and data science
computations. Designed for multi-agent scientific reasoning with rigorous
error handling and explainable results.

Author: Scientific Assistant Team
Date: January 1, 2026
"""

import functools
import inspect
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from scipy import stats, optimize
from scipy.integrate import odeint

from app.utils.logger import logger


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ComputationType(Enum):
    """Types of computations supported."""
    SYMBOLIC = "symbolic"
    NUMERICAL = "numerical"
    LINEAR_ALGEBRA = "linear_algebra"
    DATA_SCIENCE = "data_science"
    STABILITY_ANALYSIS = "stability_analysis"


class StabilityRegion(Enum):
    """Stability classification for numerical methods."""
    STABLE = "stable"
    CONDITIONALLY_STABLE = "conditionally_stable"
    UNSTABLE = "unstable"
    UNKNOWN = "unknown"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ComputationResult:
    """Structured result from a scientific computation.
    
    All computation methods return this standardized structure for
    agent-friendly consumption and explainability.
    """
    computation_type: str
    operation: str
    inputs: Dict[str, Any]
    results: Dict[str, Any]
    interpretation: str
    assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    method_used: Optional[str] = None
    latex_output: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_agent_context(self, context_key: str) -> Dict[str, Any]:
        """Convert computation result to agent context format.
        
        Args:
            context_key: Key in ResearchContext to store results
                (e.g., 'mathematical_insights', 'numerical_results', 'data_analysis')
        
        Returns:
            Dictionary ready for ResearchContext assignment
        """
        return {
            'operation': self.operation,
            'computation_type': self.computation_type,
            'success': self.success,
            'interpretation': self.interpretation,
            'results': self.results,
            'method_used': self.method_used,
            'latex_output': self.latex_output,
            'assumptions': self.assumptions,
            'warnings': self.warnings,
        }
    
    def __str__(self) -> str:
        """Human-readable summary."""
        status = "[OK]" if self.success else "[FAIL]"
        return f"{status} {self.operation}: {self.interpretation}"


# ============================================================================
# DECORATORS
# ============================================================================

def computation_wrapper(computation_type: ComputationType):
    """Decorator to standardize computation outputs and error handling.
    
    This decorator:
    - Wraps computations in try-except blocks
    - Logs computation attempts and results
    - Ensures all outputs are ComputationResult instances
    - Provides consistent error handling
    
    Args:
        computation_type: Type of computation being performed
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> ComputationResult:
            operation_name = func.__name__.replace('_', ' ').title()
            logger.info(f"Starting {computation_type.value} operation: {operation_name}")
            
            try:
                # Execute the computation
                result = func(*args, **kwargs)
                
                # Ensure result is a ComputationResult
                if not isinstance(result, ComputationResult):
                    raise TypeError(f"Function {func.__name__} must return ComputationResult")
                
                result.computation_type = computation_type.value
                result.operation = operation_name
                
                logger.info(f"[OK] {operation_name} completed successfully")
                return result
                
            except Exception as e:
                logger.error(f"[FAIL] {operation_name} failed: {str(e)}", exc_info=True)
                
                # Return structured error result
                return ComputationResult(
                    computation_type=computation_type.value,
                    operation=operation_name,
                    inputs={"args": args, "kwargs": kwargs},
                    results={},
                    interpretation=f"Computation failed: {str(e)}",
                    success=False,
                    error_message=str(e)
                )
        
        return wrapper
    return decorator


def validate_inputs(**validators):
    """Decorator to validate function inputs before computation.
    
    Args:
        **validators: Dict mapping parameter names to validation functions
    
    Example:
        @validate_inputs(expr_str=lambda x: isinstance(x, str) and len(x) > 0)
        def compute(expr_str: str): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Validate each specified parameter
                for param_name, validator in validators.items():
                    if param_name in bound_args.arguments:
                        value = bound_args.arguments[param_name]
                        if not validator(value):
                            raise ValueError(
                                f"Invalid input for parameter '{param_name}': {value}"
                            )
            except TypeError:
                # In case of staticmethod binding issues, manually validate kwargs
                for param_name, validator in validators.items():
                    if param_name in kwargs:
                        if not validator(kwargs[param_name]):
                            raise ValueError(
                                f"Invalid input for parameter '{param_name}': {kwargs[param_name]}"
                            )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def memoize_symbolic(func: Callable) -> Callable:
    """Cache symbolic computation results to avoid recomputation.
    
    Useful for expensive symbolic operations that may be repeated
    across agent calls.
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        key = (func.__name__, args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
            logger.debug(f"Cached result for {func.__name__}")
        else:
            logger.debug(f"Using cached result for {func.__name__}")
        
        return cache[key]
    
    return wrapper


# ============================================================================
# SYMBOLIC MATHEMATICS
# ============================================================================

class SymbolicMath:
    """Symbolic mathematics operations using SymPy.
    
    Provides rigorous symbolic computation with structured outputs,
    LaTeX generation, and assumption tracking.
    """
    
    @staticmethod
    def _check_linearity(expr, var) -> bool:
        """Check if expression is linear in var (safely handles transcendental functions).
        
        Args:
            expr: SymPy expression
            var: SymPy symbol
        
        Returns:
            True if linear, False otherwise
        """
        if var not in expr.free_symbols:
            return True  # Constant is linear
        
        try:
            # Try to get polynomial degree
            deg = sp.degree(expr, var)
            return deg <= 1
        except (sp.PolynomialError, ValueError, TypeError):
            # If degree() fails, it's not a polynomial (e.g., sin, cos, exp)
            return False
    
    @staticmethod
    @computation_wrapper(ComputationType.SYMBOLIC)
    def differentiate(
        expr_str: str,
        var_str: str = "x",
        order: int = 1
    ) -> ComputationResult:
        """Compute symbolic derivative with interpretation.
        
        Args:
            expr_str: Expression as string (e.g., "x**2 + sin(x)")
            var_str: Variable to differentiate with respect to
            order: Order of derivative (1 for first, 2 for second, etc.)
        
        Returns:
            ComputationResult with derivative, LaTeX, and interpretation
        """
        if not expr_str or not isinstance(expr_str, str):
            raise ValueError("Expression must be a non-empty string")
        
        # Create symbol first with real=True to avoid generator issues
        var = sp.Symbol(var_str, real=True)
        
        # Use parse_expr with transformations to properly handle functions
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, local_dict={var_str: var}, transformations=transformations)
        
        # Compute derivative
        derivative = expr
        for _ in range(order):
            derivative = sp.diff(derivative, var)
        
        # Generate LaTeX
        latex_input = sp.latex(expr)
        latex_result = sp.latex(derivative)
        
        # Simplify if possible (use trigsimp to avoid generator issues)
        try:
            simplified = sp.trigsimp(derivative)
            # If trigsimp didn't help, try basic simplification
            if simplified == derivative:
                simplified = derivative.simplify()
        except:
            # If simplification fails, use original derivative
            simplified = derivative
        
        # Helper for ordinal
        def ordinal(n: int) -> str:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n if n < 20 else n % 10, 'th')
            return f"{n}{suffix}"
        
        return ComputationResult(
            computation_type="symbolic",
            operation="Differentiation",
            inputs={
                "expression": expr_str,
                "variable": var_str,
                "order": order
            },
            results={
                "derivative": str(derivative),
                "simplified": str(simplified),
                "is_constant": derivative == 0,
                "is_linear": SymbolicMath._check_linearity(simplified, var)
            },
            interpretation=f"The {ordinal(order)} derivative of {expr_str} with respect to {var_str} is {simplified}",
            latex_output=f"\\frac{{d^{order} }}{{d{var_str}^{order}}} \\left( {latex_input} \\right) = {latex_result}",
            method_used="SymPy symbolic differentiation"
        )
    
    @staticmethod
    @computation_wrapper(ComputationType.SYMBOLIC)
    def integrate(
        expr_str: str,
        var_str: str = "x",
        limits: Optional[Tuple[float, float]] = None
    ) -> ComputationResult:
        """Compute symbolic integral with interpretation.
        
        Args:
            expr_str: Expression to integrate
            var_str: Integration variable
            limits: Optional (lower, upper) bounds for definite integral
        
        Returns:
            ComputationResult with integral and interpretation
        """
        if not expr_str or not isinstance(expr_str, str):
            raise ValueError("Expression must be a non-empty string")
        
        # Create symbol first with real=True
        var = sp.Symbol(var_str, real=True)
        
        # Use parse_expr with transformations
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, local_dict={var_str: var}, transformations=transformations)
        
        if limits is None:
            # Indefinite integral
            result = sp.integrate(expr, var)
            integral_type = "indefinite"
            interpretation = f"The indefinite integral of {expr_str} with respect to {var_str} is {result} + C"
            latex_result = sp.latex(result) + " + C"
        else:
            # Definite integral
            lower, upper = limits
            result = sp.integrate(expr, (var, lower, upper))
            integral_type = "definite"
            interpretation = f"The definite integral of {expr_str} from {lower} to {upper} is {result}"
            latex_result = sp.latex(result)
        
        latex_input = sp.latex(expr)
        
        return ComputationResult(
            computation_type="symbolic",
            operation="Integration",
            inputs={
                "expression": expr_str,
                "variable": var_str,
                "limits": limits,
                "type": integral_type
            },
            results={
                "integral": str(result),
                "simplified": str(sp.simplify(result)),
                "numerical_value": float(result) if result.is_number else None
            },
            interpretation=interpretation,
            latex_output=f"\\int {latex_input} \\, d{var_str} = {latex_result}",
            method_used="SymPy symbolic integration"
        )
    
    @staticmethod
    @computation_wrapper(ComputationType.SYMBOLIC)
    def taylor_series(
        expr_str: str,
        var_str: str = "x",
        point: float = 0,
        order: int = 5
    ) -> ComputationResult:
        """Compute Taylor series expansion.
        
        Args:
            expr_str: Expression to expand
            var_str: Expansion variable
            point: Point of expansion
            order: Number of terms
        
        Returns:
            ComputationResult with series expansion
        """
        if not expr_str or not isinstance(expr_str, str):
            raise ValueError("Expression must be a non-empty string")
        
        # Create symbol first with real=True
        var = sp.Symbol(var_str, real=True)
        
        # Use parse_expr with transformations
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, local_dict={var_str: var}, transformations=transformations)
        
        # Compute Taylor series
        series = sp.series(expr, var, point, n=order + 1).removeO()
        
        # Extract coefficients
        coefficients = [series.coeff(var, i) for i in range(order + 1)]
        
        return ComputationResult(
            computation_type="symbolic",
            operation="Taylor Series Expansion",
            inputs={
                "expression": expr_str,
                "variable": var_str,
                "point": point,
                "order": order
            },
            results={
                "series": str(series),
                "coefficients": [str(c) for c in coefficients],
                "truncation_error": f"O({var_str}^{order + 1})"
            },
            interpretation=f"Taylor expansion of {expr_str} around {var_str}={point} up to order {order}",
            latex_output=sp.latex(series),
            assumptions=[
                f"Valid in convergence radius around {var_str} = {point}",
                f"Higher order terms neglected (O({var_str}^{order + 1}))"
            ]
        )
    
    @staticmethod
    @computation_wrapper(ComputationType.SYMBOLIC)
    def solve_equation(
        expr_str: str,
        var_str: str = "x",
        domain: str = "real"
    ) -> ComputationResult:
        """Solve equation symbolically.
        
        Args:
            expr_str: Equation (set to zero) or expression
            var_str: Variable to solve for
            domain: 'real', 'complex', or 'positive'
        
        Returns:
            ComputationResult with solutions
        """
        if not expr_str or not isinstance(expr_str, str):
            raise ValueError("Expression must be a non-empty string")
        
        # Create symbol with domain constraints
        var = sp.Symbol(var_str, real=(domain == "real"), positive=(domain == "positive"))
        
        # Use parse_expr with transformations
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, local_dict={var_str: var}, transformations=transformations)
        
        # Solve equation
        solutions = sp.solve(expr, var)
        
        # Classify solutions
        real_solutions = [sol for sol in solutions if sol.is_real]
        complex_solutions = [sol for sol in solutions if not sol.is_real]
        
        return ComputationResult(
            computation_type="symbolic",
            operation="Equation Solving",
            inputs={
                "equation": expr_str,
                "variable": var_str,
                "domain": domain
            },
            results={
                "solutions": [str(sol) for sol in solutions],
                "num_solutions": len(solutions),
                "real_solutions": [str(sol) for sol in real_solutions],
                "complex_solutions": [str(sol) for sol in complex_solutions],
                "solution_types": {
                    "real": len(real_solutions),
                    "complex": len(complex_solutions)
                }
            },
            interpretation=f"Found {len(solutions)} solution(s) for {expr_str} = 0",
            latex_output=sp.latex(expr) + " = 0",
            assumptions=[f"Solutions in {domain} domain"]
        )


# ============================================================================
# NUMERICAL ANALYSIS
# ============================================================================

class NumericalAnalysis:
    """Numerical methods and stability analysis.
    
    Provides stability analysis, convergence tests, and numerical
    method evaluation for ODEs and PDEs.
    """
    
    @staticmethod
    @computation_wrapper(ComputationType.STABILITY_ANALYSIS)
    def euler_stability_analysis(
        lambda_val: complex,
        dt: float,
        method: str = "explicit"
    ) -> ComputationResult:
        """Analyze stability of Euler method for test equation dy/dt = λy.
        
        Args:
            lambda_val: Eigenvalue λ (can be complex)
            dt: Time step size
            method: 'explicit' or 'implicit'
        
        Returns:
            ComputationResult with stability analysis
        """
        z = lambda_val * dt
        
        if method == "explicit":
            # Amplification factor: 1 + z
            amplification = 1 + z
            stability_condition = abs(amplification) <= 1
            stability_region_desc = "|1 + λΔt| ≤ 1"
            
        elif method == "implicit":
            # Amplification factor: 1/(1 - z)
            amplification = 1 / (1 - z)
            stability_condition = abs(amplification) <= 1
            stability_region_desc = "|1/(1 - λΔt)| ≤ 1"
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Determine stability
        if stability_condition:
            stability = StabilityRegion.STABLE
            interpretation = f"Method is STABLE for λ={lambda_val}, Δt={dt}"
        else:
            stability = StabilityRegion.UNSTABLE
            interpretation = f"Method is UNSTABLE for λ={lambda_val}, Δt={dt}"
        
        return ComputationResult(
            computation_type="stability_analysis",
            operation=f"{method.title()} Euler Stability",
            inputs={
                "lambda": complex(lambda_val),
                "dt": dt,
                "method": method
            },
            results={
                "amplification_factor": complex(amplification),
                "amplification_magnitude": abs(amplification),
                "is_stable": stability_condition,
                "stability_region": stability.value,
                "z_parameter": complex(z)
            },
            interpretation=interpretation,
            assumptions=[
                "Test equation: dy/dt = λy",
                "Linear stability analysis",
                f"Stability criterion: {stability_region_desc}"
            ],
            method_used=f"{method.title()} Euler method"
        )
    
    @staticmethod
    @computation_wrapper(ComputationType.NUMERICAL)
    def richardson_extrapolation(
        f: Callable,
        h_values: List[float],
        target_accuracy: float = 1e-6
    ) -> ComputationResult:
        """Richardson extrapolation for convergence acceleration.
        
        Args:
            f: Function that takes step size h and returns approximation
            h_values: List of decreasing step sizes
            target_accuracy: Desired accuracy
        
        Returns:
            ComputationResult with extrapolated value
        """
        n = len(h_values)
        R = np.zeros((n, n))
        
        # Fill first column with function evaluations
        for i in range(n):
            R[i, 0] = f(h_values[i])
        
        # Richardson extrapolation
        for j in range(1, n):
            for i in range(n - j):
                R[i, j] = (4**j * R[i+1, j-1] - R[i, j-1]) / (4**j - 1)
        
        # Best estimate
        extrapolated = R[0, -1]
        
        # Estimate error
        if n > 1:
            estimated_error = abs(R[0, -1] - R[0, -2])
        else:
            estimated_error = None
        
        return ComputationResult(
            computation_type="numerical",
            operation="Richardson Extrapolation",
            inputs={
                "h_values": h_values,
                "num_levels": n
            },
            results={
                "extrapolated_value": float(extrapolated),
                "estimated_error": float(estimated_error) if estimated_error else None,
                "converged": estimated_error < target_accuracy if estimated_error else None,
                "extrapolation_table": R.tolist()
            },
            interpretation=f"Extrapolated value: {extrapolated:.10f}",
            assumptions=[
                "Function has asymptotic expansion in powers of h²",
                "Richardson extrapolation assumes h → 0"
            ],
            method_used="Richardson extrapolation"
        )

    @staticmethod
    @computation_wrapper(ComputationType.NUMERICAL)
    def root_finding(
        f: Callable,
        a: Optional[float] = None,
        b: Optional[float] = None,
        x0: Optional[float] = None,
        df: Optional[Callable] = None,
        method: str = "bisection",
        max_iterations: int = 100,
        tolerance: float = 1e-8
    ) -> ComputationResult:
        """Find roots of a scalar function using classic methods.
        
        Supports:
        - Bisection: requires bracket [a, b] with f(a)·f(b) < 0
        - Newton-Raphson: requires initial guess x0 (and df if available)
        """

        if not callable(f):
            raise ValueError("f must be a callable taking a single float argument")

        method = method.lower()
        history = []
        root = None
        converged = False
        reason = "max_iterations"

        if method == "bisection":
            if a is None or b is None:
                raise ValueError("Bisection requires bracket [a, b]")
            fa, fb = f(a), f(b)
            if fa * fb > 0:
                raise ValueError("Function must have opposite signs at a and b for bisection")

            left, right = float(a), float(b)
            for k in range(max_iterations):
                mid = 0.5 * (left + right)
                fm = f(mid)
                history.append({"iteration": k, "x": mid, "f(x)": fm})

                if abs(fm) < tolerance or abs(right - left) < tolerance:
                    root = mid
                    converged = True
                    reason = "tolerance"
                    break
                if fa * fm < 0:
                    right = mid
                    fb = fm
                else:
                    left = mid
                    fa = fm

            if root is None:
                root = mid

        elif method in {"newton", "newton-raphson"}:
            if x0 is None:
                raise ValueError("Newton method requires an initial guess x0")
            if df is None:
                # Numerical derivative if not provided
                def df(z, h=1e-6):
                    return (f(z + h) - f(z - h)) / (2 * h)

            x = float(x0)
            for k in range(max_iterations):
                fx = f(x)
                dfx = df(x)
                history.append({"iteration": k, "x": x, "f(x)": fx, "f'(x)": dfx})
                if abs(dfx) < 1e-14:
                    reason = "zero_derivative"
                    break
                step = fx / dfx
                x_new = x - step
                if abs(step) < tolerance or abs(fx) < tolerance:
                    root = x_new
                    converged = True
                    reason = "tolerance"
                    break
                x = x_new
            if root is None:
                root = x
        else:
            raise ValueError(f"Unknown root-finding method: {method}")

        final_residual = abs(f(root)) if root is not None else None

        interpretation = (
            f"Root ≈ {root:.6g} (residual {final_residual:.2e if final_residual is not None else 'N/A'})"
        )
        if not converged:
            interpretation += f"; did not meet tolerance ({reason})"

        return ComputationResult(
            computation_type="numerical",
            operation=f"Root Finding ({method})",
            inputs={
                "method": method,
                "a": a,
                "b": b,
                "x0": x0,
                "tolerance": tolerance,
                "max_iterations": max_iterations
            },
            results={
                "root": float(root) if root is not None else None,
                "residual": float(final_residual) if final_residual is not None else None,
                "converged": converged,
                "reason": reason,
                "iterations": len(history),
                "history": history
            },
            interpretation=interpretation,
            assumptions=[
                "Function is continuous on bracket for bisection",
                "Derivative exists and is non-zero near root for Newton"
            ],
            method_used=f"{method.title()} root finding"
        )

    @staticmethod
    @computation_wrapper(ComputationType.NUMERICAL)
    def rk4_solve(
        ode_func: Callable[[float, np.ndarray], np.ndarray],
        t_span: Tuple[float, float],
        y0: Union[float, List[float], np.ndarray],
        step_size: float = 0.01
    ) -> ComputationResult:
        """Integrate ODE system using classical Runge-Kutta 4.
        
        Args:
            ode_func: Callable f(t, y) returning dy/dt
            t_span: (t0, t_end)
            y0: Initial state (scalar or vector)
            step_size: Integration step size
        """

        t0, t_end = t_span
        if step_size <= 0:
            raise ValueError("step_size must be positive")

        y = np.atleast_1d(np.array(y0, dtype=float))
        t_values = [float(t0)]
        y_values = [y.tolist()]

        t = float(t0)
        num_steps = int(np.ceil((t_end - t0) / step_size))

        for _ in range(num_steps):
            if t >= t_end:
                break
            h = min(step_size, t_end - t)
            k1 = np.array(ode_func(t, y))
            k2 = np.array(ode_func(t + 0.5 * h, y + 0.5 * h * k1))
            k3 = np.array(ode_func(t + 0.5 * h, y + 0.5 * h * k2))
            k4 = np.array(ode_func(t + h, y + h * k3))

            y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            t = t + h

            t_values.append(float(t))
            y_values.append(y.tolist())

        interpretation = (
            f"Integrated from t={t0} to t={t_end} with {len(t_values)-1} steps; "
            f"final state: {y_values[-1]}"
        )

        return ComputationResult(
            computation_type="numerical",
            operation="Runge-Kutta 4 ODE Solve",
            inputs={
                "t_span": t_span,
                "y0": np.array(y0).tolist() if hasattr(y0, "tolist") else y0,
                "step_size": step_size
            },
            results={
                "t": t_values,
                "y": y_values,
                "num_steps": len(t_values) - 1,
                "final_state": y_values[-1]
            },
            interpretation=interpretation,
            assumptions=[
                "ODE function is Lipschitz continuous for stability",
                "Fixed step size RK4 method"
            ],
            method_used="Classical RK4"
        )
    
    @staticmethod
    def convergence_rate_generator(
        f: Callable,
        h_start: float,
        h_end: float,
        num_steps: int = 10
    ) -> Generator[Dict[str, float], None, None]:
        """Generate convergence rate data points.
        
        This generator yields convergence data for plotting and analysis
        without storing all results in memory.
        
        Args:
            f: Function to evaluate at different step sizes
            h_start: Starting step size
            h_end: Ending step size
            num_steps: Number of step sizes to test
        
        Yields:
            Dict with h, result, and estimated_error
        """
        h_values = np.logspace(np.log10(h_start), np.log10(h_end), num_steps)
        previous_result = None
        
        for h in h_values:
            result = f(h)
            
            error = None
            if previous_result is not None:
                error = abs(result - previous_result)
            
            yield {
                "h": h,
                "result": result,
                "estimated_error": error,
                "log_h": np.log10(h),
                "log_error": np.log10(error) if error and error > 0 else None
            }
            
            previous_result = result


# ============================================================================
# LINEAR ALGEBRA
# ============================================================================

class LinearAlgebra:
    """Linear algebra operations and analysis.
    
    Provides matrix operations with numerical stability indicators
    and condition number analysis.
    """
    
    @staticmethod
    @computation_wrapper(ComputationType.LINEAR_ALGEBRA)
    def matrix_analysis(matrix_data: Union[List, np.ndarray]) -> ComputationResult:
        """Comprehensive matrix analysis.
        
        Args:
            matrix_data: Matrix as list of lists or numpy array
        
        Returns:
            ComputationResult with complete matrix properties
        """
        if not isinstance(matrix_data, (list, np.ndarray)):
            raise ValueError("Matrix data must be a list or numpy array")
        
        A = np.array(matrix_data, dtype=float)
        m, n = A.shape
        
        results = {
            "shape": (m, n),
            "is_square": m == n,
        }
        
        # Square matrix properties
        if m == n:
            results["determinant"] = float(np.linalg.det(A))
            results["rank"] = int(np.linalg.matrix_rank(A))
            results["trace"] = float(np.trace(A))
            results["is_singular"] = abs(results["determinant"]) < 1e-10
            
            # Eigenvalues
            eigenvalues = np.linalg.eigvals(A)
            results["eigenvalues"] = eigenvalues.tolist()
            results["spectral_radius"] = float(np.max(np.abs(eigenvalues)))
            
            # Condition number
            try:
                cond = np.linalg.cond(A)
                results["condition_number"] = float(cond)
                results["is_well_conditioned"] = cond < 100
                results["is_ill_conditioned"] = cond > 1e10
            except:
                results["condition_number"] = None
            
            # Definiteness
            try:
                if np.allclose(A, A.T):
                    eigvals_real = np.real(eigenvalues)
                    if np.all(eigvals_real > 0):
                        results["definiteness"] = "positive_definite"
                    elif np.all(eigvals_real < 0):
                        results["definiteness"] = "negative_definite"
                    else:
                        results["definiteness"] = "indefinite"
                else:
                    results["definiteness"] = "not_symmetric"
            except:
                results["definiteness"] = "unknown"
        
        # Frobenius norm
        results["frobenius_norm"] = float(np.linalg.norm(A, 'fro'))
        
        # Interpretation
        interpretation_parts = [f"{m}×{n} matrix"]
        if results.get("is_singular"):
            interpretation_parts.append("singular (non-invertible)")
        if results.get("is_ill_conditioned"):
            interpretation_parts.append("ill-conditioned (numerically unstable)")
        
        interpretation = ", ".join(interpretation_parts)
        
        warnings = []
        if results.get("is_ill_conditioned"):
            warnings.append("Matrix is ill-conditioned - numerical computations may be inaccurate")
        if results.get("is_singular"):
            warnings.append("Matrix is singular - cannot be inverted")
        
        return ComputationResult(
            computation_type="linear_algebra",
            operation="Matrix Analysis",
            inputs={"matrix": matrix_data, "shape": (m, n)},
            results=results,
            interpretation=interpretation,
            warnings=warnings,
            method_used="NumPy linear algebra"
        )
    
    @staticmethod
    @computation_wrapper(ComputationType.LINEAR_ALGEBRA)
    def solve_linear_system(
        A: Union[List, np.ndarray],
        b: Union[List, np.ndarray],
        method: str = "direct"
    ) -> ComputationResult:
        """Solve linear system Ax = b.
        
        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            method: 'direct', 'least_squares', or 'iterative'
        
        Returns:
            ComputationResult with solution and residual analysis
        """
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        
        if method == "direct":
            x = np.linalg.solve(A, b)
        elif method == "least_squares":
            x = np.linalg.lstsq(A, b, rcond=None)[0]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Compute residual
        residual = b - A @ x
        residual_norm = np.linalg.norm(residual)
        b_norm = np.linalg.norm(b)
        relative_residual = residual_norm / b_norm if b_norm > 0 else 0

        return ComputationResult(
            computation_type="linear_algebra",
            operation="Linear System Solution",
            inputs={
                "A_shape": A.shape,
                "b_shape": b.shape,
                "method": method
            },
            results={
                "solution": x.tolist(),
                "residual_norm": float(residual_norm),
                "relative_residual": float(relative_residual),
                "is_accurate": relative_residual < 1e-6
            },
            interpretation=f"Solution computed with {method} method, relative residual: {relative_residual:.2e}",
            method_used=f"{method} solver"
        )

    @staticmethod
    @computation_wrapper(ComputationType.LINEAR_ALGEBRA)
    def svd_analysis(matrix_data: Union[List, np.ndarray]) -> ComputationResult:
        """Singular Value Decomposition with conditioning insights."""
        if not isinstance(matrix_data, (list, np.ndarray)):
            raise ValueError("Matrix data must be a list or numpy array")

        A = np.array(matrix_data, dtype=float)
        U, S, Vt = np.linalg.svd(A, full_matrices=False)

        energy = np.cumsum(S**2) / np.sum(S**2)
        condition_number = float(S[0] / S[-1]) if S[-1] != 0 else np.inf

        interpretation = (
            f"Rank={np.linalg.matrix_rank(A)}, cond={condition_number:.2e}, "
            f"energy (first 3): {energy[:3].round(3).tolist()}"
        )

        return ComputationResult(
            computation_type="linear_algebra",
            operation="SVD Analysis",
            inputs={"shape": A.shape},
            results={
                "U": U.tolist(),
                "S": S.tolist(),
                "Vt": Vt.tolist(),
                "condition_number": condition_number,
                "energy_cumulative": energy.tolist(),
                "rank": int(np.linalg.matrix_rank(A))
            },
            interpretation=interpretation,
            method_used="Singular Value Decomposition"
        )

    @staticmethod
    @computation_wrapper(ComputationType.LINEAR_ALGEBRA)
    def pca(
        data: Union[List, np.ndarray],
        n_components: int = 2,
        scale: bool = True
    ) -> ComputationResult:
        """Principal Component Analysis using eigen decomposition.

        Args:
            data: Samples x features
            n_components: Number of principal components to keep
            scale: Whether to standardize features
        """
        X = np.array(data, dtype=float)
        if X.ndim != 2:
            raise ValueError("data must be 2D (samples, features)")
        n_samples, n_features = X.shape
        if n_components < 1 or n_components > n_features:
            raise ValueError("n_components must be between 1 and number of features")

        # Center
        mean = X.mean(axis=0)
        X_centered = X - mean

        # Scale if requested
        if scale:
            std = X.std(axis=0)
            std[std == 0] = 1.0
            X_centered = X_centered / std
        else:
            std = np.ones_like(mean)

        cov = np.cov(X_centered, rowvar=False)
        eigvals, eigvecs = np.linalg.eigh(cov)
        idx = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx]
        eigvecs = eigvecs[:, idx]

        explained_variance = eigvals
        explained_variance_ratio = eigvals / eigvals.sum()

        components = eigvecs[:, :n_components]
        scores = X_centered @ components

        interpretation = (
            f"PCA with {n_components} components captures "
            f"{explained_variance_ratio[:n_components].sum():.2%} variance"
        )

        return ComputationResult(
            computation_type="linear_algebra",
            operation="PCA",
            inputs={
                "n_samples": n_samples,
                "n_features": n_features,
                "n_components": n_components,
                "scaled": scale
            },
            results={
                "components": components.tolist(),
                "explained_variance": explained_variance.tolist(),
                "explained_variance_ratio": explained_variance_ratio.tolist(),
                "scores": scores.tolist(),
                "mean": mean.tolist(),
                "std": std.tolist()
            },
            interpretation=interpretation,
            method_used="Eigenvalue decomposition of covariance"
        )


# ============================================================================
# DATA SCIENCE
# ============================================================================

class DataScienceTools:
    """Statistical analysis and data science computations.
    
    Provides regression, hypothesis testing, and statistical summaries
    with interpretations.
    """
    
    @staticmethod
    @computation_wrapper(ComputationType.DATA_SCIENCE)
    def linear_regression(
        x_data: Union[List, np.ndarray],
        y_data: Union[List, np.ndarray],
        confidence_level: float = 0.95
    ) -> ComputationResult:
        """Perform linear regression with statistical analysis.
        
        Args:
            x_data: Independent variable data
            y_data: Dependent variable data
            confidence_level: Confidence level for intervals
        
        Returns:
            ComputationResult with regression analysis
        """
        if not isinstance(x_data, (list, np.ndarray)) or len(x_data) <= 1:
            raise ValueError("x_data must be a list or array with at least 2 elements")
        if not isinstance(y_data, (list, np.ndarray)) or len(y_data) <= 1:
            raise ValueError("y_data must be a list or array with at least 2 elements")
        
        x = np.array(x_data)
        y = np.array(y_data)
        n = len(x)
        
        # Perform regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Predictions
        y_pred = slope * x + intercept
        residuals = y - y_pred
        rss = np.sum(residuals**2)
        tss = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (rss / tss) if tss > 0 else 0
        
        # Standard errors
        se_slope = std_err
        se_intercept = se_slope * np.sqrt(np.sum(x**2) / n)
        
        # Confidence intervals
        from scipy.stats import t
        t_val = t.ppf((1 + confidence_level) / 2, n - 2)
        ci_slope = (slope - t_val * se_slope, slope + t_val * se_slope)
        ci_intercept = (intercept - t_val * se_intercept, intercept + t_val * se_intercept)
        
        # Interpretation
        interpretation = (
            f"Linear fit: y = {slope:.4f}x + {intercept:.4f} "
            f"(R² = {r_squared:.4f}, p = {p_value:.4e})"
        )
        
        return ComputationResult(
            computation_type="data_science",
            operation="Linear Regression",
            inputs={
                "n_points": n,
                "x_range": (float(np.min(x)), float(np.max(x))),
                "y_range": (float(np.min(y)), float(np.max(y)))
            },
            results={
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_squared),
                "correlation": float(r_value),
                "p_value": float(p_value),
                "std_error": float(std_err),
                "confidence_intervals": {
                    "slope": ci_slope,
                    "intercept": ci_intercept
                },
                "equation": f"y = {slope:.4f}x + {intercept:.4f}",
                "residuals": residuals.tolist()
            },
            interpretation=interpretation,
            assumptions=[
                "Linear relationship between variables",
                "Homoscedasticity (constant variance)",
                "Independence of observations",
                "Normality of residuals"
            ],
            method_used="Ordinary Least Squares (OLS)"
        )
    
    @staticmethod
    @computation_wrapper(ComputationType.DATA_SCIENCE)
    def logistic_regression(
        X_data: Union[List, np.ndarray],
        y_data: Union[List, np.ndarray],
        learning_rate: float = 0.01,
        max_iterations: int = 1000,
        tolerance: float = 1e-6
    ) -> ComputationResult:
        """Perform logistic regression with gradient descent.
        
        Minimizes the binary cross-entropy cost function:
        J(θ) = -1/m * Σ[y*log(h(x)) + (1-y)*log(1-h(x))]
        where h(x) = 1/(1 + exp(-θ'x)) is the sigmoid function
        
        Args:
            X_data: Feature matrix (n_samples, n_features)
            y_data: Binary labels (0 or 1)
            learning_rate: Step size for gradient descent
            max_iterations: Maximum number of iterations
            tolerance: Convergence threshold for cost function
        
        Returns:
            ComputationResult with trained parameters and metrics
        """
        if not isinstance(X_data, (list, np.ndarray)):
            raise ValueError("X_data must be a list or numpy array")
        if not isinstance(y_data, (list, np.ndarray)):
            raise ValueError("y_data must be a list or numpy array")
        
        X = np.array(X_data)
        y = np.array(y_data).reshape(-1, 1)
        
        # Add bias term (intercept)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        m, n = X.shape
        X_bias = np.c_[np.ones((m, 1)), X]
        
        # Initialize parameters
        theta = np.zeros((n + 1, 1))
        
        # Helper functions
        def sigmoid(z):
            """Sigmoid activation function."""
            return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
        
        def compute_cost(X, y, theta):
            """Compute binary cross-entropy cost."""
            m = len(y)
            h = sigmoid(X @ theta)
            epsilon = 1e-15  # Avoid log(0)
            h = np.clip(h, epsilon, 1 - epsilon)
            cost = -1/m * np.sum(y * np.log(h) + (1 - y) * np.log(1 - h))
            return cost
        
        def compute_gradient(X, y, theta):
            """Compute gradient of cost function."""
            m = len(y)
            h = sigmoid(X @ theta)
            gradient = 1/m * X.T @ (h - y)
            return gradient
        
        # Gradient descent
        cost_history = []
        theta_history = []
        converged = False
        
        for iteration in range(max_iterations):
            # Compute current cost
            current_cost = compute_cost(X_bias, y, theta)
            cost_history.append(current_cost)
            theta_history.append(theta.copy())
            
            # Compute gradient
            gradient = compute_gradient(X_bias, y, theta)
            
            # Update parameters
            theta = theta - learning_rate * gradient
            
            # Check convergence
            if iteration > 0 and abs(cost_history[-2] - cost_history[-1]) < tolerance:
                converged = True
                break
        
        # Final predictions
        h_final = sigmoid(X_bias @ theta)
        predictions = (h_final >= 0.5).astype(int)
        
        # Compute metrics
        accuracy = np.mean(predictions == y)
        
        # Confusion matrix elements
        tp = np.sum((predictions == 1) & (y == 1))
        tn = np.sum((predictions == 0) & (y == 0))
        fp = np.sum((predictions == 1) & (y == 0))
        fn = np.sum((predictions == 0) & (y == 1))
        
        # Precision, Recall, F1-score
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Interpretation
        interpretation = (
            f"Logistic regression converged in {len(cost_history)} iterations. "
            f"Final cost: {cost_history[-1]:.6f}, Accuracy: {accuracy:.4f}, F1-score: {f1_score:.4f}"
        )
        
        warnings = []
        if not converged:
            warnings.append(f"Did not converge after {max_iterations} iterations")
        if accuracy < 0.6:
            warnings.append("Low accuracy - consider feature engineering or different model")
        
        return ComputationResult(
            computation_type="data_science",
            operation="Logistic Regression",
            inputs={
                "n_samples": m,
                "n_features": n,
                "learning_rate": learning_rate,
                "max_iterations": max_iterations
            },
            results={
                "parameters": theta.flatten().tolist(),
                "bias": float(theta[0, 0]),
                "weights": theta[1:].flatten().tolist(),
                "final_cost": float(cost_history[-1]),
                "initial_cost": float(cost_history[0]),
                "cost_reduction": float(cost_history[0] - cost_history[-1]),
                "iterations": len(cost_history),
                "converged": converged,
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1_score),
                "confusion_matrix": {
                    "true_positive": int(tp),
                    "true_negative": int(tn),
                    "false_positive": int(fp),
                    "false_negative": int(fn)
                },
                "cost_history": [float(c) for c in cost_history[-10:]],  # Last 10 iterations
                "predictions": predictions.flatten().tolist()
            },
            interpretation=interpretation,
            warnings=warnings,
            assumptions=[
                "Binary classification (labels are 0 or 1)",
                "Features are linearly separable (or approximately)",
                "Sigmoid function as activation: σ(z) = 1/(1 + e^(-z))",
                "Cross-entropy cost function minimized",
                f"Learning rate: {learning_rate}"
            ],
            method_used="Gradient Descent with Binary Cross-Entropy"
        )
    
    @staticmethod
    def gradient_descent_steps(
        X_data: Union[List, np.ndarray],
        y_data: Union[List, np.ndarray],
        learning_rate: float = 0.01,
        max_iterations: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """Generator that yields gradient descent steps for logistic regression.
        
        Useful for visualization and monitoring convergence in real-time.
        
        Args:
            X_data: Feature matrix
            y_data: Binary labels
            learning_rate: Step size
            max_iterations: Number of iterations to generate
        
        Yields:
            Dict with iteration, cost, gradient_norm, and parameters
        """
        X = np.array(X_data)
        y = np.array(y_data).reshape(-1, 1)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        m, n = X.shape
        X_bias = np.c_[np.ones((m, 1)), X]
        
        theta = np.zeros((n + 1, 1))
        
        def sigmoid(z):
            return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
        
        def compute_cost(X, y, theta):
            m = len(y)
            h = sigmoid(X @ theta)
            epsilon = 1e-15
            h = np.clip(h, epsilon, 1 - epsilon)
            return -1/m * np.sum(y * np.log(h) + (1 - y) * np.log(1 - h))
        
        def compute_gradient(X, y, theta):
            m = len(y)
            h = sigmoid(X @ theta)
            return 1/m * X.T @ (h - y)
        
        for iteration in range(max_iterations):
            cost = compute_cost(X_bias, y, theta)
            gradient = compute_gradient(X_bias, y, theta)
            gradient_norm = np.linalg.norm(gradient)
            
            # Make predictions
            h = sigmoid(X_bias @ theta)
            predictions = (h >= 0.5).astype(int)
            accuracy = np.mean(predictions == y)
            
            yield {
                "iteration": iteration,
                "cost": float(cost),
                "gradient_norm": float(gradient_norm),
                "parameters": theta.flatten().tolist(),
                "accuracy": float(accuracy),
                "learning_rate": learning_rate
            }
            
            # Update parameters
            theta = theta - learning_rate * gradient
    
    @staticmethod
    @computation_wrapper(ComputationType.DATA_SCIENCE)
    def statistical_summary(data: Union[List, np.ndarray]) -> ComputationResult:
        """Comprehensive statistical summary of data.
        
        Args:
            data: Numerical data array
        
        Returns:
            ComputationResult with statistical measures
        """
        data = np.array(data)
        n = len(data)
        
        # Basic statistics
        mean = np.mean(data)
        median = np.median(data)
        std = np.std(data, ddof=1)
        var = np.var(data, ddof=1)
        
        # Quartiles
        q1, q3 = np.percentile(data, [25, 75])
        iqr = q3 - q1
        
        # Range
        min_val = np.min(data)
        max_val = np.max(data)
        range_val = max_val - min_val
        
        # Skewness and kurtosis
        skewness = float(stats.skew(data))
        kurtosis = float(stats.kurtosis(data))
        
        # Outlier detection (IQR method)
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = data[(data < lower_fence) | (data > upper_fence)]
        
        return ComputationResult(
            computation_type="data_science",
            operation="Statistical Summary",
            inputs={"n_points": n},
            results={
                "count": n,
                "mean": float(mean),
                "median": float(median),
                "std": float(std),
                "variance": float(var),
                "min": float(min_val),
                "max": float(max_val),
                "range": float(range_val),
                "q1": float(q1),
                "q3": float(q3),
                "iqr": float(iqr),
                "skewness": skewness,
                "kurtosis": kurtosis,
                "num_outliers": len(outliers),
                "outliers": outliers.tolist() if len(outliers) > 0 else []
            },
            interpretation=f"Dataset: n={n}, μ={mean:.2f}, σ={std:.2f}, outliers={len(outliers)}",
            method_used="Descriptive statistics"
        )


# ============================================================================
# UNIFIED FACADE
# ============================================================================

class ScientificCalculator:
    """Unified facade for all scientific computations.
    
    This class provides a single entry point for agents to access
    all computational capabilities: symbolic math, numerical analysis,
    linear algebra, and data science.
    
    Usage:
        calc = ScientificCalculator()
        result = calc.symbolic.differentiate("x**2")
        print(result.to_dict())
    """
    
    def __init__(self):
        """Initialize calculator with all computation modules."""
        self.symbolic = SymbolicMath()
        self.numerical = NumericalAnalysis()
        self.linear_algebra = LinearAlgebra()
        self.data_science = DataScienceTools()
        
        logger.info("ScientificCalculator initialized")
    
    def quick_eval(self, expr_str: str, **substitutions) -> float:
        """Quick numerical evaluation of expression.
        
        Args:
            expr_str: Expression as string
            **substitutions: Variable values (e.g., x=5, y=3)
        
        Returns:
            Numerical value
        """
        # Create symbols for all substitutions
        symbols = {var: sp.Symbol(var, real=True) for var in substitutions.keys()}
        
        # Use parse_expr with transformations
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, local_dict=symbols, transformations=transformations)
        
        # Apply substitutions
        for var, val in substitutions.items():
            expr = expr.subs(symbols[var], val)
        return float(expr)
    
    def batch_differentiate(
        self,
        expressions: List[str],
        var: str = "x"
    ) -> Generator[ComputationResult, None, None]:
        """Generator for batch differentiation.
        
        Useful for agents processing multiple expressions efficiently
        without storing all results in memory.
        
        Args:
            expressions: List of expression strings
            var: Variable to differentiate with respect to
        
        Yields:
            ComputationResult for each expression
        """
        for expr in expressions:
            yield self.symbolic.differentiate(expr, var)
    
    def gradient_descent_visualization(
        self,
        X: Union[List, np.ndarray],
        y: Union[List, np.ndarray],
        learning_rate: float = 0.01,
        max_iterations: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """Generator for gradient descent steps in logistic regression.
        
        Useful for visualizing convergence and monitoring training.
        
        Args:
            X: Feature matrix
            y: Binary labels
            learning_rate: Step size
            max_iterations: Number of steps
        
        Yields:
            Dict with iteration metrics
        """
        yield from self.data_science.gradient_descent_steps(X, y, learning_rate, max_iterations)
    
    def __repr__(self) -> str:
        return (
            "ScientificCalculator(\n"
            "  symbolic=SymbolicMath(),\n"
            "  numerical=NumericalAnalysis(),\n"
            "  linear_algebra=LinearAlgebra(),\n"
            "  data_science=DataScienceTools()\n"
            ")"
        )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_calculator() -> ScientificCalculator:
    """Factory function to create calculator instance.
    
    Returns:
        Configured ScientificCalculator instance
    """
    return ScientificCalculator()


# Example usage for agents
if __name__ == "__main__":
    # Initialize calculator
    calc = create_calculator()
    
    # Example 1: Symbolic differentiation
    result = calc.symbolic.differentiate("x**2 + sin(x)", "x")
    print(result)
    print(result.latex_output)
    
    # Example 2: Stability analysis
    stability = calc.numerical.euler_stability_analysis(
        lambda_val=-1.0,
        dt=0.1,
        method="explicit"
    )
    print(stability)
    
    # Example 3: Matrix analysis
    matrix = [[2, 1], [1, 3]]
    analysis = calc.linear_algebra.matrix_analysis(matrix)
    print(analysis)
    
    # Example 4: Linear regression
    x = [1, 2, 3, 4, 5]
    y = [2.1, 3.9, 6.2, 8.1, 9.8]
    regression = calc.data_science.linear_regression(x, y)
    print(regression)
    
    # Example 5: Using generator for batch operations
    expressions = ["x**2", "sin(x)", "exp(x)"]
    for result in calc.batch_differentiate(expressions):
        print(f"  {result.interpretation}")
