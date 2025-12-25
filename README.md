# Scientific Assistant

A high-level scientific computing assistant for applied mathematics and data science, built with Python and modern package management using `uv`.

## Overview

This assistant provides comprehensive tools for researchers and practitioners in applied mathematics, numerical analysis, statistical modeling, and data science. It integrates the most powerful Python scientific libraries into a unified, easy-to-use interface.

## Features

### 🔬 Mathematical Analysis
- Symbolic and numerical differentiation/integration
- Optimization problems (constrained and unconstrained)
- Linear algebra operations (eigenvalues, matrix solving)
- Taylor series expansions
- Advanced calculus operations

### 🧮 Numerical Experimentation
- ODE and PDE solvers
- Numerical integration methods
- Interpolation techniques
- Monte Carlo simulations
- Finite difference methods

### 📊 Statistical & ML Modeling
- Linear and logistic regression
- Random forests (classification and regression)
- Time series analysis (ARIMA models)
- Cross-validation and model evaluation
- Comprehensive statistical modeling with statsmodels

### 📈 Data Science Tools
- Data loading and exploration
- Data cleaning and preprocessing
- Advanced visualization (distributions, correlations, time series)
- Summary statistics and group analysis
- Integration with pandas, matplotlib, and seaborn

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/Geobatpo07/scientific-assistant.git
cd scientific-assistant

# Install with uv
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

## Quick Start

### Python API

```python
from scientific_assistant import ScientificAssistant

# Create assistant instance
assistant = ScientificAssistant()

# Mathematical Analysis
derivative = assistant.analysis.differentiate("x**2 + 3*x + 2", "x")
print(derivative)  # 2*x + 3

integral = assistant.analysis.integrate("x**2", "x", (0, 1))
print(integral)  # 1/3

# Numerical Experimentation
result = assistant.numerical.numerical_integration(lambda x: x**2, 0, 1)
print(result)  # ~0.333

# Statistical Modeling
import numpy as np
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])
model_result = assistant.modeling.linear_regression(X, y)
print(f"R² score: {model_result['r2_score']}")

# Data Science
import pandas as pd
df = pd.DataFrame({
    'age': [25, 30, 35, 40, 45],
    'income': [30000, 40000, 50000, 60000, 70000]
})
info = assistant.data.load_and_explore(df)
print(info['description'])
```

### Command Line Interface

```bash
# Display information about available modules
scientific-assistant --info

# Start interactive session with assistant loaded
scientific-assistant --interactive

# Show version
scientific-assistant --version
```

## Examples

### Example 1: Optimization Problem

```python
from scientific_assistant import ScientificAssistant
import numpy as np

assistant = ScientificAssistant()

# Minimize (x-1)² + (y-2)²
def objective(x):
    return (x[0] - 1)**2 + (x[1] - 2)**2

result = assistant.analysis.optimize_function(objective, [0, 0])
print(f"Optimal point: {result.x}")  # [1., 2.]
```

### Example 2: Solving ODEs

```python
from scientific_assistant import ScientificAssistant
import numpy as np
import matplotlib.pyplot as plt

assistant = ScientificAssistant()

# Solve dy/dt = -0.5*y (exponential decay)
def exponential_decay(t, y):
    return -0.5 * y

t_eval = np.linspace(0, 10, 100)
result = assistant.numerical.solve_ode(
    exponential_decay, 
    [1.0], 
    (0, 10), 
    t_eval=t_eval
)

plt.plot(result.t, result.y[0])
plt.xlabel('Time')
plt.ylabel('y')
plt.title('Exponential Decay')
plt.show()
```

### Example 3: Machine Learning Pipeline

```python
from scientific_assistant import ScientificAssistant
from sklearn.datasets import load_iris

assistant = ScientificAssistant()

# Load dataset
iris = load_iris()
X, y = iris.data, iris.target

# Train random forest classifier
result = assistant.modeling.random_forest(X, y, task='classification', n_estimators=100)
print(f"Test accuracy: {result['test_score']:.3f}")
print(f"Feature importance: {result['feature_importance']}")
```

### Example 4: Data Analysis

```python
from scientific_assistant import ScientificAssistant
import pandas as pd
import numpy as np

assistant = ScientificAssistant()

# Create sample dataset
np.random.seed(42)
df = pd.DataFrame({
    'temperature': np.random.normal(25, 5, 100),
    'humidity': np.random.normal(60, 10, 100),
    'pressure': np.random.normal(1013, 5, 100)
})

# Explore data
info = assistant.data.load_and_explore(df)
print(f"Dataset shape: {info['shape']}")
print(info['description'])

# Correlation analysis
corr_result = assistant.data.correlation_analysis(df, plot=True)
print(corr_result['correlation_matrix'])

# Summary statistics
stats = assistant.data.summary_statistics(df, 'temperature')
print(f"Mean temperature: {stats['mean']:.2f}")
print(f"Std deviation: {stats['std']:.2f}")
```

## Dependencies

- **numpy** (≥1.26.0): Numerical computing
- **scipy** (≥1.11.0): Scientific computing
- **sympy** (≥1.12): Symbolic mathematics
- **pandas** (≥2.1.0): Data manipulation
- **matplotlib** (≥3.8.0): Visualization
- **seaborn** (≥0.13.0): Statistical visualization
- **scikit-learn** (≥1.3.0): Machine learning
- **statsmodels** (≥0.14.0): Statistical modeling
- **jupyter** (≥1.0.0): Interactive notebooks
- **ipython** (≥8.18.0): Enhanced Python shell

## Development

### Setting up development environment

```bash
# Clone repository
git clone https://github.com/Geobatpo07/scientific-assistant.git
cd scientific-assistant

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Project Structure

```
scientific-assistant/
├── scientific_assistant/
│   ├── __init__.py           # Package initialization
│   ├── assistant.py          # Main assistant class
│   ├── cli.py                # Command-line interface
│   ├── analysis/             # Mathematical analysis module
│   │   └── __init__.py
│   ├── numerical/            # Numerical experimentation module
│   │   └── __init__.py
│   ├── modeling/             # Statistical/ML modeling module
│   │   └── __init__.py
│   └── data_science/         # Data science tools module
│       └── __init__.py
├── tests/                    # Test suite
├── examples/                 # Example notebooks and scripts
├── pyproject.toml           # Project configuration
├── README.md                # This file
└── LICENSE                  # License file
```

## Use Cases

- **Research**: Rapid prototyping of mathematical models and numerical experiments
- **Data Analysis**: Comprehensive exploratory data analysis and statistical modeling
- **Machine Learning**: Quick model training and evaluation
- **Education**: Learning and teaching scientific computing concepts
- **Engineering**: Solving optimization problems and numerical simulations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Built with the powerful Python scientific computing stack:
- NumPy, SciPy, SymPy for mathematical operations
- Pandas for data manipulation
- Matplotlib and Seaborn for visualization
- Scikit-learn and Statsmodels for statistical modeling

---

**Note**: This is an assistant tool designed to help researchers and practitioners. Always validate results for critical applications.