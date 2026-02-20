"""
Example 1: Mathematical Analysis
=================================

This example demonstrates the mathematical analysis capabilities of the
Scientific Assistant, including calculus, optimization, and linear algebra.
"""

from scientific_assistant import ScientificAssistant
import numpy as np
import matplotlib.pyplot as plt

# Initialize the assistant
assistant = ScientificAssistant()

print("=" * 60)
print("EXAMPLE 1: MATHEMATICAL ANALYSIS")
print("=" * 60)

# 1. Symbolic Differentiation
print("\n1. Symbolic Differentiation")
print("-" * 40)
expression = "x**3 + 2*x**2 + 3*x + 1"
derivative = assistant.analysis.differentiate(expression, "x")
print(f"f(x) = {expression}")
print(f"f'(x) = {derivative}")

# 2. Symbolic Integration
print("\n2. Symbolic Integration")
print("-" * 40)
expression = "sin(x)"
integral = assistant.analysis.integrate(expression, "x")
print(f"∫ {expression} dx = {integral}")

# Definite integral
definite = assistant.analysis.integrate("x**2", "x", (0, 2))
print(f"∫₀² x² dx = {definite} = {float(definite):.4f}")

# 3. Optimization
print("\n3. Function Optimization")
print("-" * 40)

# Minimize the Rosenbrock function
def rosenbrock(x):
    return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2

result = assistant.analysis.optimize_function(rosenbrock, [0, 0])
print(f"Minimizing Rosenbrock function: (1-x)² + 100(y-x²)²")
print(f"Minimum found at: x = {result.x[0]:.6f}, y = {result.x[1]:.6f}")
print(f"Function value: {result.fun:.6f}")

# 4. Linear Algebra
print("\n4. Linear Algebra")
print("-" * 40)

# Solve a system of linear equations
A = [[3, 1], [1, 2]]
b = [9, 8]
x = assistant.analysis.solve_linear_system(A, b)
print(f"Solving system: 3x + y = 9, x + 2y = 8")
print(f"Solution: x = {x[0]:.2f}, y = {x[1]:.2f}")

# Eigenvalues and eigenvectors
matrix = [[4, -2], [1, 1]]
eigenvalues, eigenvectors = assistant.analysis.eigenvalues(matrix)
print(f"\nEigenvalues of [[4, -2], [1, 1]]:")
print(f"λ₁ = {eigenvalues[0]:.4f}, λ₂ = {eigenvalues[1]:.4f}")

# 5. Taylor Series
print("\n5. Taylor Series Expansion")
print("-" * 40)
taylor = assistant.analysis.taylor_series("exp(x)", "x", 0, 5)
print(f"Taylor series of e^x around x=0 (order 5):")
print(f"{taylor}")

print("\n" + "=" * 60)
print("Example complete!")
print("=" * 60)
