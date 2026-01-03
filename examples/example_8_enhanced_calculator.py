"""
Example demonstrating the enhanced research-grade calculator.py

This script showcases:
- Structured ComputationResult outputs
- Decorators for validation and logging
- Generators for efficient batch processing
- Comprehensive error handling
- Multi-class architecture with specialized domains
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.tools.calculator import (
    create_calculator,
    ComputationResult,
    ComputationType,
    StabilityRegion
)


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}\n")


def demonstrate_symbolic_math():
    """Demonstrate symbolic mathematics capabilities."""
    print_section("SYMBOLIC MATHEMATICS")
    
    calc = create_calculator()
    
    # Example 1: Differentiation
    print("1. Differentiation:")
    result = calc.symbolic.differentiate("x**3 + 2*x**2 + x", "x", order=1)
    print(f"   {result}")
    print(f"   LaTeX: {result.latex_output}")
    print(f"   Simplified: {result.results['simplified']}")
    print(f"   JSON: {result.to_dict()['results']}\n")
    
    # Example 2: Integration
    print("2. Integration (definite):")
    result = calc.symbolic.integrate("x**2", "x", limits=(0, 1))
    print(f"   {result}")
    print(f"   Result: {result.results['integral']}")
    print(f"   Numerical value: {result.results['numerical_value']}\n")
    
    # Example 3: Taylor series
    print("3. Taylor Series:")
    result = calc.symbolic.taylor_series("sin(x)", "x", point=0, order=5)
    print(f"   {result}")
    print(f"   Series: {result.results['series']}")
    print(f"   Assumptions: {result.assumptions}\n")
    
    # Example 4: Equation solving
    print("4. Equation Solving:")
    result = calc.symbolic.solve_equation("x**2 - 4", "x", domain="real")
    print(f"   {result}")
    print(f"   Solutions: {result.results['solutions']}")
    print(f"   Real: {result.results['real_solutions']}\n")


def demonstrate_numerical_analysis():
    """Demonstrate numerical analysis capabilities."""
    print_section("NUMERICAL ANALYSIS")
    
    calc = create_calculator()
    
    # Example 1: Euler method stability
    print("1. Euler Method Stability Analysis:")
    result = calc.numerical.euler_stability_analysis(
        lambda_val=-5.0,
        dt=0.1,
        method="explicit"
    )
    print(f"   {result}")
    print(f"   Stability: {result.results['stability_region']}")
    print(f"   Amplification factor: {result.results['amplification_magnitude']:.4f}")
    print(f"   Is stable: {result.results['is_stable']}\n")
    
    # Example 2: Richardson extrapolation
    print("2. Richardson Extrapolation:")
    # Simple function for testing: approximate π using trapezoid rule
    import numpy as np
    
    def integrate_circle(h):
        """Approximate π/4 using trapezoid rule on sqrt(1-x²)."""
        x = np.arange(0, 1, h)
        y = np.sqrt(1 - x**2)
        # Use trapezoid rule: integrate.trapezoid for numpy >= 1.25
        try:
            from numpy import trapezoid
            return trapezoid(y, x)
        except ImportError:
            return np.trapz(y, x)
    
    h_values = [0.1, 0.05, 0.025]
    result = calc.numerical.richardson_extrapolation(integrate_circle, h_values)
    print(f"   {result}")
    if result.success:
        print(f"   Extrapolated: {result.results['extrapolated_value']:.10f}")
        print(f"   True π/4: {np.pi / 4:.10f}")
        print(f"   Error: {abs(result.results['extrapolated_value'] - np.pi/4):.2e}\n")
    else:
        print(f"   Error: {result.error_message}\n")
    
    # Example 3: Convergence generator
    print("3. Convergence Rate Analysis (Generator):")
    print("   h          Result       Error")
    print("   " + "-" * 45)
    
    for data in calc.numerical.convergence_rate_generator(integrate_circle, 0.1, 0.001, 5):
        error_str = f"{data['estimated_error']:.6f}" if data['estimated_error'] else "N/A"
        print(f"   {data['h']:.5f}    {data['result']:.8f}   {error_str}")
    print()


def demonstrate_linear_algebra():
    """Demonstrate linear algebra capabilities."""
    print_section("LINEAR ALGEBRA")
    
    calc = create_calculator()
    
    # Example 1: Matrix analysis
    print("1. Matrix Analysis:")
    matrix = [
        [4, 1, 2],
        [1, 3, 0],
        [2, 0, 5]
    ]
    result = calc.linear_algebra.matrix_analysis(matrix)
    print(f"   {result}")
    print(f"   Determinant: {result.results['determinant']:.4f}")
    print(f"   Condition number: {result.results['condition_number']:.4f}")
    print(f"   Eigenvalues: {[f'{e:.4f}' for e in result.results['eigenvalues']]}")
    print(f"   Definiteness: {result.results['definiteness']}\n")
    
    # Example 2: Linear system solving
    print("2. Linear System Ax = b:")
    A = [[3, 1], [1, 2]]
    b = [9, 8]
    result = calc.linear_algebra.solve_linear_system(A, b, method="direct")
    print(f"   {result}")
    print(f"   Solution: {result.results['solution']}")
    print(f"   Residual norm: {result.results['residual_norm']:.2e}")
    print(f"   Accurate: {result.results['is_accurate']}\n")


def demonstrate_data_science():
    """Demonstrate data science capabilities."""
    print_section("DATA SCIENCE")
    
    calc = create_calculator()
    
    # Example 1: Linear regression
    print("1. Linear Regression:")
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [2.1, 4.0, 5.8, 8.2, 9.9, 12.1, 14.0, 16.2, 17.8, 20.1]
    
    result = calc.data_science.linear_regression(x, y, confidence_level=0.95)
    print(f"   {result}")
    print(f"   Equation: {result.results['equation']}")
    print(f"   R²: {result.results['r_squared']:.4f}")
    print(f"   p-value: {result.results['p_value']:.4e}")
    print(f"   95% CI slope: ({result.results['confidence_intervals']['slope'][0]:.4f}, "
          f"{result.results['confidence_intervals']['slope'][1]:.4f})\n")
    
    # Example 2: Statistical summary
    print("2. Statistical Summary:")
    import numpy as np
    data = np.random.normal(100, 15, 1000)  # Mean 100, std 15, 1000 points
    
    result = calc.data_science.statistical_summary(data)
    print(f"   {result}")
    print(f"   Mean: {result.results['mean']:.2f}")
    print(f"   Median: {result.results['median']:.2f}")
    print(f"   Std Dev: {result.results['std']:.2f}")
    print(f"   Range: [{result.results['min']:.2f}, {result.results['max']:.2f}]")
    print(f"   Skewness: {result.results['skewness']:.4f}")
    print(f"   Outliers: {result.results['num_outliers']}\n")


def demonstrate_generators():
    """Demonstrate generator usage for batch processing."""
    print_section("GENERATOR BATCH PROCESSING")
    
    calc = create_calculator()
    
    print("Batch Differentiation (Memory-Efficient):")
    expressions = [
        "x**2",
        "sin(x)",
        "exp(x)",
        "log(x)",
        "x**3 + 2*x**2 + x + 1",
        "cos(x)**2 + sin(x)**2"
    ]
    
    print("   Expression              -> Derivative")
    print("   " + "-" * 60)
    
    for result in calc.batch_differentiate(expressions, "x"):
        if result.success:
            expr = result.inputs['expression']
            deriv = result.results['simplified']
            print(f"   {expr:22s} -> {deriv}")
        else:
            print(f"   [FAIL] {result.error_message}")
    print()


def demonstrate_error_handling():
    """Demonstrate robust error handling."""
    print_section("ERROR HANDLING & VALIDATION")
    
    calc = create_calculator()
    
    print("1. Invalid input (empty string):")
    result = calc.symbolic.differentiate("", "x")
    print(f"   Success: {result.success}")
    print(f"   Error: {result.error_message}\n")
    
    print("2. Invalid matrix (singular system):")
    A = [[1, 2], [2, 4]]  # Singular matrix
    b = [1, 2]
    result = calc.linear_algebra.solve_linear_system(A, b)
    print(f"   Success: {result.success}")
    if not result.success:
        print(f"   Error: {result.error_message}\n")
    
    print("3. Division by zero in expression:")
    result = calc.symbolic.differentiate("1/x", "x")
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Derivative: {result.results['derivative']}\n")
    else:
        print(f"   Error: {result.error_message}\n")


def demonstrate_agent_integration():
    """Demonstrate how agents would use the calculator."""
    print_section("AGENT INTEGRATION EXAMPLE")
    
    calc = create_calculator()
    
    print("Agent Query: 'What is the derivative of x²sin(x)?'")
    print("-" * 70)
    
    # Agent calls calculator
    result = calc.symbolic.differentiate("x**2 * sin(x)", "x")
    
    # Agent receives structured output
    print(f"[OK] Computation Type: {result.computation_type}")
    print(f"[OK] Operation: {result.operation}")
    print(f"[OK] Success: {result.success}")
    print(f"\nInterpretation for user:")
    print(f"  {result.interpretation}")
    print(f"\nLaTeX for rendering:")
    print(f"  {result.latex_output}")
    print(f"\nMethod used:")
    print(f"  {result.method_used}")
    print(f"\nStructured results (JSON-serializable):")
    print(f"  {result.to_dict()['results']}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RESEARCH-GRADE SCIENTIFIC CALCULATOR DEMONSTRATION".center(70))
    print("Enhanced with Decorators, Generators, and Structured Outputs".center(70))
    print("=" * 70)
    
    try:
        demonstrate_symbolic_math()
        demonstrate_numerical_analysis()
        demonstrate_linear_algebra()
        demonstrate_data_science()
        demonstrate_generators()
        demonstrate_error_handling()
        demonstrate_agent_integration()
        
        print("\n" + "=" * 70)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY".center(70))
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
