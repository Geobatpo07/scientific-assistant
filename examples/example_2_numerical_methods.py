"""
Example 2: Numerical Experimentation
=====================================

This example demonstrates numerical methods including ODE solving,
numerical integration, interpolation, and Monte Carlo simulation.
"""

from scientific_assistant import ScientificAssistant
import numpy as np
import matplotlib.pyplot as plt

# Initialize the assistant
assistant = ScientificAssistant()

print("=" * 60)
print("EXAMPLE 2: NUMERICAL EXPERIMENTATION")
print("=" * 60)

# 1. Solving ODEs
print("\n1. Solving Ordinary Differential Equations")
print("-" * 40)

# Example: Population growth model dy/dt = 0.5*y
def population_growth(t, y):
    return 0.5 * y

t_span = (0, 10)
t_eval = np.linspace(0, 10, 100)
result = assistant.numerical.solve_ode(
    population_growth, 
    [1.0],  # Initial population
    t_span,
    t_eval=t_eval
)

print("Solving dy/dt = 0.5*y with y(0) = 1")
print(f"Solution at t=10: y(10) = {result.y[0][-1]:.4f}")
print(f"Analytical solution: e^(0.5*10) = {np.exp(5):.4f}")

# 2. Numerical Integration
print("\n2. Numerical Integration")
print("-" * 40)

# Integrate a Gaussian function
def gaussian(x):
    return np.exp(-x**2)

result = assistant.numerical.numerical_integration(gaussian, -2, 2)
print(f"∫₋₂² e^(-x²) dx ≈ {result:.6f}")
print(f"Analytical value: √π * erf(2) ≈ {np.sqrt(np.pi) * np.math.erf(2):.6f}")

# 3. Interpolation
print("\n3. Data Interpolation")
print("-" * 40)

# Create sample data points
x_data = np.array([0, 1, 2, 3, 4])
y_data = np.array([0, 1, 4, 9, 16])  # y = x^2

# Create interpolation function
f_interp = assistant.numerical.interpolate_data(x_data, y_data, kind='cubic')

# Interpolate at new points
x_new = np.array([0.5, 1.5, 2.5, 3.5])
y_new = f_interp(x_new)

print("Interpolating data points: (0,0), (1,1), (2,4), (3,9), (4,16)")
print("Interpolated values:")
for x, y in zip(x_new, y_new):
    print(f"  f({x}) ≈ {y:.4f} (exact: {x**2:.4f})")

# 4. Monte Carlo Simulation
print("\n4. Monte Carlo Simulation")
print("-" * 40)

# Estimate the area under x^2 from 0 to 1
result = assistant.numerical.monte_carlo_simulation(
    lambda x: x**2,
    n_samples=10000,
    bounds=[(0, 1)],
    seed=42
)

print("Estimating ∫₀¹ x² dx using Monte Carlo (10,000 samples)")
print(f"Estimated value: {result['mean']:.6f} ± {result['std']:.6f}")
print(f"Analytical value: 1/3 = {1/3:.6f}")

# 5. Finite Differences
print("\n5. Finite Difference Approximation")
print("-" * 40)

# Approximate derivative of x^3 at x=2
func = lambda x: x**3
x_point = 2.0
derivative = assistant.numerical.finite_difference(func, x_point)

print(f"Approximating derivative of f(x) = x³ at x = {x_point}")
print(f"Numerical derivative: {derivative:.6f}")
print(f"Analytical derivative: 3x² = {3 * x_point**2:.6f}")

print("\n" + "=" * 60)
print("Example complete!")
print("=" * 60)
