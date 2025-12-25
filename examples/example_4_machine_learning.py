"""
Example 4: Machine Learning and Statistical Modeling
=====================================================

This example demonstrates statistical modeling and machine learning
capabilities of the Scientific Assistant.
"""

from scientific_assistant import ScientificAssistant
import numpy as np
from sklearn.datasets import make_classification, make_regression
import matplotlib.pyplot as plt

# Initialize the assistant
assistant = ScientificAssistant()

print("=" * 60)
print("EXAMPLE 4: MACHINE LEARNING & STATISTICAL MODELING")
print("=" * 60)

# 1. Linear Regression
print("\n1. Linear Regression")
print("-" * 40)

# Generate synthetic regression data
X_reg, y_reg = make_regression(n_samples=100, n_features=1, noise=10, random_state=42)

result = assistant.modeling.linear_regression(X_reg, y_reg, return_metrics=True)
print(f"Linear regression model trained")
print(f"R² score: {result['r2_score']:.4f}")
print(f"Coefficient: {result['coefficients'][0]:.4f}")
print(f"Intercept: {result['intercept']:.4f}")

# 2. Logistic Regression
print("\n2. Logistic Regression (Binary Classification)")
print("-" * 40)

# Generate synthetic classification data
X_class, y_class = make_classification(
    n_samples=200, 
    n_features=5, 
    n_informative=3,
    n_redundant=1,
    n_classes=2,
    random_state=42
)

result = assistant.modeling.logistic_regression(X_class, y_class)
print(f"Logistic regression model trained")
print(f"Training accuracy: {result['train_accuracy']:.4f}")
print(f"Test accuracy: {result['test_accuracy']:.4f}")
print(f"Number of features: {len(result['coefficients'][0])}")

# 3. Random Forest Classifier
print("\n3. Random Forest Classifier")
print("-" * 40)

result = assistant.modeling.random_forest(
    X_class, 
    y_class, 
    task='classification',
    n_estimators=50
)
print(f"Random forest classifier trained (50 trees)")
print(f"Training accuracy: {result['train_score']:.4f}")
print(f"Test accuracy: {result['test_score']:.4f}")
print(f"Feature importance: {result['feature_importance']}")

# 4. Random Forest Regressor
print("\n4. Random Forest Regressor")
print("-" * 40)

X_reg_multi, y_reg_multi = make_regression(
    n_samples=200,
    n_features=5,
    n_informative=3,
    noise=10,
    random_state=42
)

result = assistant.modeling.random_forest(
    X_reg_multi,
    y_reg_multi,
    task='regression',
    n_estimators=50
)
print(f"Random forest regressor trained (50 trees)")
print(f"Training R² score: {result['train_score']:.4f}")
print(f"Test R² score: {result['test_score']:.4f}")

# 5. OLS Regression with statsmodels
print("\n5. Ordinary Least Squares (OLS) Regression")
print("-" * 40)

# Use smaller dataset for OLS
X_ols = X_reg[:50]
y_ols = y_reg[:50]

result = assistant.modeling.ols_regression(X_ols, y_ols)
print("OLS regression summary:")
print(result.summary())

# 6. Time Series Analysis
print("\n6. Time Series Analysis (ARIMA)")
print("-" * 40)

# Generate synthetic time series data
np.random.seed(42)
time_series = np.cumsum(np.random.randn(50)) + 10

try:
    result = assistant.modeling.time_series_arima(time_series, order=(1, 1, 1))
    print(f"ARIMA(1,1,1) model fitted")
    print(f"AIC: {result['aic']:.4f}")
    print(f"BIC: {result['bic']:.4f}")
except Exception as e:
    print(f"Time series fitting encountered an issue (this is normal for some data): {e}")

# 7. Cross-validation
print("\n7. Cross-Validation")
print("-" * 40)

from sklearn.linear_model import Ridge

model = Ridge(alpha=1.0)
result = assistant.modeling.cross_validate(model, X_reg_multi, y_reg_multi, cv=5)
print(f"5-Fold Cross-validation with Ridge regression")
print(f"Cross-validation scores: {result['scores']}")
print(f"Mean score: {result['mean_score']:.4f} ± {result['std_score']:.4f}")

print("\n" + "=" * 60)
print("Example complete!")
print("=" * 60)
