# Quick Start Guide

## Installation

### Prerequisites
- Python 3.12 or later
- `uv` package manager (or pip)

### Install with uv

```bash
# Clone the repository
git clone https://github.com/Geobatpo07/scientific-assistant.git
cd scientific-assistant

# Create virtual environment
uv venv

# Install the package
uv pip install -e .
```

### Install with pip

```bash
pip install -e .
```

## Basic Usage

### 1. Python API

```python
from scientific_assistant import ScientificAssistant

# Create assistant instance
assistant = ScientificAssistant()

# Show available capabilities
assistant.info()
```

### 2. Command Line Interface

```bash
# Display information
scientific-assistant --info

# Start interactive session
scientific-assistant --interactive

# Show version
scientific-assistant --version
```

## Quick Examples

### Mathematical Analysis

```python
from scientific_assistant import ScientificAssistant

assistant = ScientificAssistant()

# Differentiation
derivative = assistant.analysis.differentiate("x**2 + 3*x + 2", "x")
print(derivative)  # 2*x + 3

# Integration
integral = assistant.analysis.integrate("x**2", "x", (0, 1))
print(integral)  # 1/3

# Optimization
def objective(x):
    return (x[0] - 1)**2 + (x[1] - 2)**2

result = assistant.analysis.optimize_function(objective, [0, 0])
print(result.x)  # [1., 2.]
```

### Numerical Methods

```python
# Solve an ODE: dy/dt = -0.5*y
def decay(t, y):
    return -0.5 * y

result = assistant.numerical.solve_ode(decay, [1.0], (0, 10))

# Numerical integration
value = assistant.numerical.numerical_integration(lambda x: x**2, 0, 1)
print(f"Integral ≈ {value:.6f}")  # ≈ 0.333333
```

### Machine Learning

```python
import numpy as np

# Linear regression
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

result = assistant.modeling.linear_regression(X, y)
print(f"R² score: {result['r2_score']}")
print(f"Coefficients: {result['coefficients']}")

# Classification with Random Forest
from sklearn.datasets import load_iris
iris = load_iris()

result = assistant.modeling.random_forest(
    iris.data, 
    iris.target, 
    task='classification'
)
print(f"Test accuracy: {result['test_score']:.3f}")
```

### Data Science

```python
import pandas as pd
import numpy as np

# Create sample data
df = pd.DataFrame({
    'age': np.random.randint(20, 70, 100),
    'income': np.random.normal(50000, 15000, 100)
})

# Explore data
info = assistant.data.load_and_explore(df)
print(info['description'])

# Clean data
df_clean = assistant.data.clean_data(df, fill_na_method='mean')

# Summary statistics
stats = assistant.data.summary_statistics(df_clean, 'income')
print(f"Mean: ${stats['mean']:.2f}")
print(f"Std: ${stats['std']:.2f}")

# Correlation analysis
corr = assistant.data.correlation_analysis(df_clean, plot=True)
```

## Running Examples

The repository includes several complete examples:

```bash
# Mathematical analysis
python examples/example_1_mathematical_analysis.py

# Numerical methods
python examples/example_2_numerical_methods.py

# Data science
python examples/example_3_data_science.py

# Machine learning
python examples/example_4_machine_learning.py
```

## Running Tests

```bash
# Install pytest (if not already installed)
uv pip install pytest

# Run all tests
pytest tests/ -v
```

## Module Overview

### `assistant.analysis`
- **differentiate()**: Symbolic differentiation
- **integrate()**: Symbolic and definite integration
- **optimize_function()**: Function optimization
- **solve_linear_system()**: Solve Ax = b
- **eigenvalues()**: Compute eigenvalues/eigenvectors
- **taylor_series()**: Taylor series expansion

### `assistant.numerical`
- **solve_ode()**: Solve ordinary differential equations
- **numerical_integration()**: Numerical integration
- **interpolate_data()**: Data interpolation
- **monte_carlo_simulation()**: Monte Carlo methods
- **finite_difference()**: Numerical derivatives

### `assistant.modeling`
- **linear_regression()**: Linear regression
- **logistic_regression()**: Logistic regression
- **random_forest()**: Random forest (classification/regression)
- **time_series_arima()**: ARIMA time series models
- **ols_regression()**: OLS with statsmodels
- **cross_validate()**: Cross-validation

### `assistant.data`
- **load_and_explore()**: Data exploration
- **clean_data()**: Data cleaning
- **visualize_distribution()**: Distribution plots
- **correlation_analysis()**: Correlation analysis
- **time_series_plot()**: Time series visualization
- **summary_statistics()**: Statistical summaries
- **group_analysis()**: Group-by operations

## Next Steps

1. Explore the examples in the `examples/` directory
2. Read the full documentation in `README.md`
3. Check out the test suite in `tests/` for more usage examples
4. Start building your own scientific applications!

## Getting Help

- Check the docstrings: `help(assistant.analysis.differentiate)`
- Run `assistant.info()` to see available modules
- Read the examples in the `examples/` directory
- Check the test cases in `tests/` for more examples

## Tips

- Use the interactive mode for exploratory work: `scientific-assistant --interactive`
- All functions have detailed docstrings with examples
- Combine modules for complex workflows
- Use matplotlib/seaborn for visualization alongside the built-in plotting tools
