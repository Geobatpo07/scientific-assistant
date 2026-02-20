"""Test suite for the Scientific Assistant."""

import pytest
import numpy as np
from scientific_assistant import ScientificAssistant


@pytest.fixture
def assistant():
    """Create an assistant instance for testing."""
    return ScientificAssistant()


class TestMathematicalAnalysis:
    """Tests for mathematical analysis module."""
    
    def test_differentiate(self, assistant):
        """Test symbolic differentiation."""
        result = assistant.analysis.differentiate("x**2 + 3*x + 2", "x")
        assert str(result) == "2*x + 3"
    
    def test_integrate(self, assistant):
        """Test symbolic integration."""
        result = assistant.analysis.integrate("x**2", "x")
        assert "x**3" in str(result)
    
    def test_definite_integral(self, assistant):
        """Test definite integration."""
        result = assistant.analysis.integrate("x**2", "x", (0, 1))
        assert abs(float(result) - 1/3) < 1e-10
    
    def test_optimize_function(self, assistant):
        """Test function optimization."""
        result = assistant.analysis.optimize_function(
            lambda x: (x[0] - 1)**2 + (x[1] - 2)**2, 
            [0, 0]
        )
        assert np.allclose(result.x, [1.0, 2.0], atol=1e-5)
    
    def test_solve_linear_system(self, assistant):
        """Test linear system solver."""
        A = [[2, 1], [1, 3]]
        b = [5, 7]
        x = assistant.analysis.solve_linear_system(A, b)
        assert np.allclose(x, [1.6, 1.8])


class TestNumericalExperimentation:
    """Tests for numerical experimentation module."""
    
    def test_numerical_integration(self, assistant):
        """Test numerical integration."""
        result = assistant.numerical.numerical_integration(lambda x: x**2, 0, 1)
        assert abs(result - 1/3) < 1e-5
    
    def test_solve_ode(self, assistant):
        """Test ODE solver."""
        def exponential_growth(t, y):
            return 0.5 * y
        
        result = assistant.numerical.solve_ode(
            exponential_growth, 
            [1.0], 
            (0, 2),
            t_eval=[0, 1, 2]
        )
        assert result.success
        assert len(result.y[0]) == 3
    
    def test_finite_difference(self, assistant):
        """Test finite difference method."""
        derivative = assistant.numerical.finite_difference(lambda x: x**2, 2.0)
        assert abs(derivative - 4.0) < 1e-4


class TestModelingTools:
    """Tests for modeling tools module."""
    
    def test_linear_regression(self, assistant):
        """Test linear regression."""
        X = np.array([[1], [2], [3], [4]])
        y = np.array([2, 4, 6, 8])
        result = assistant.modeling.linear_regression(X, y)
        assert result['r2_score'] > 0.99
        assert np.allclose(result['coefficients'], [2.0], atol=0.1)
    
    def test_logistic_regression(self, assistant):
        """Test logistic regression."""
        X = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])
        y = np.array([0, 0, 0, 1, 1, 1])
        result = assistant.modeling.logistic_regression(X, y, test_size=0.3)
        assert 'model' in result
        assert 'train_accuracy' in result


class TestDataScienceTools:
    """Tests for data science tools module."""
    
    def test_load_and_explore(self, assistant):
        """Test data exploration."""
        import pandas as pd
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'income': [30000, 40000, 50000, 60000, 70000]
        })
        info = assistant.data.load_and_explore(df)
        assert info['shape'] == (5, 2)
        assert 'age' in info['columns']
        assert 'income' in info['columns']
    
    def test_summary_statistics(self, assistant):
        """Test summary statistics."""
        data = [1, 2, 3, 4, 5]
        stats = assistant.data.summary_statistics(data)
        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['count'] == 5


def test_assistant_info(assistant):
    """Test assistant info method."""
    info = assistant.info()
    assert "Scientific Assistant" in info
    assert "analysis" in info
    assert "numerical" in info
    assert "modeling" in info
    assert "data" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
