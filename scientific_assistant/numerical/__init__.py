"""Numerical experimentation tools for simulations and numerical methods."""

import numpy as np
from scipy import integrate, interpolate
from scipy.integrate import odeint, solve_ivp


class NumericalExperimentation:
    """
    Tools for numerical experimentation including:
    - ODE and PDE solvers
    - Numerical integration
    - Interpolation
    - Monte Carlo simulations
    """
    
    def __init__(self):
        """Initialize numerical experimentation tools."""
        pass
    
    def solve_ode(self, func, y0, t_span, t_eval=None, method='RK45'):
        """
        Solve an ordinary differential equation.
        
        Args:
            func (callable): The ODE function dy/dt = func(t, y)
            y0 (array-like): Initial conditions
            t_span (tuple): Time span (t_start, t_end)
            t_eval (array-like, optional): Times at which to store solution
            method (str): Integration method
            
        Returns:
            scipy.integrate.OdeResult: Solution object
            
        Example:
            >>> ne = NumericalExperimentation()
            >>> def exponential_growth(t, y):
            ...     return 0.5 * y
            >>> result = ne.solve_ode(exponential_growth, [1.0], (0, 10))
        """
        return solve_ivp(func, t_span, y0, method=method, t_eval=t_eval, dense_output=True)
    
    def numerical_integration(self, func, a, b, method='quad'):
        """
        Numerically integrate a function.
        
        Args:
            func (callable): Function to integrate
            a (float): Lower limit
            b (float): Upper limit
            method (str): Integration method ('quad', 'trapezoid', 'simpson')
            
        Returns:
            float: Integration result
            
        Example:
            >>> ne = NumericalExperimentation()
            >>> result = ne.numerical_integration(lambda x: x**2, 0, 1)
            >>> print(result)  # Should be close to 1/3
        """
        if method == 'quad':
            result, error = integrate.quad(func, a, b)
            return result
        elif method == 'trapezoid':
            # Use trapezoidal rule
            n_points = 100
            x = np.linspace(a, b, n_points)
            y = func(x)
            return integrate.trapezoid(y, x)
        else:
            # Simpson's rule
            n_points = 100
            x = np.linspace(a, b, n_points)
            y = func(x)
            return integrate.simpson(y, x=x)
    
    def interpolate_data(self, x, y, kind='cubic'):
        """
        Interpolate data points.
        
        Args:
            x (array-like): x coordinates
            y (array-like): y coordinates
            kind (str): Type of interpolation ('linear', 'cubic', 'quadratic')
            
        Returns:
            callable: Interpolation function
            
        Example:
            >>> ne = NumericalExperimentation()
            >>> x = [0, 1, 2, 3]
            >>> y = [0, 1, 4, 9]
            >>> f = ne.interpolate_data(x, y, kind='cubic')
            >>> print(f(1.5))
        """
        return interpolate.interp1d(x, y, kind=kind, fill_value='extrapolate')
    
    def monte_carlo_simulation(self, func, n_samples=10000, bounds=None, seed=None):
        """
        Perform Monte Carlo simulation.
        
        Args:
            func (callable): Function to evaluate
            n_samples (int): Number of samples
            bounds (list of tuples): Bounds for each dimension [(min, max), ...]
            seed (int, optional): Random seed for reproducibility
            
        Returns:
            dict: Results including mean, std, and samples
            
        Example:
            >>> ne = NumericalExperimentation()
            >>> # Estimate area under curve
            >>> result = ne.monte_carlo_simulation(
            ...     lambda x: x**2, 
            ...     n_samples=10000,
            ...     bounds=[(0, 1)]
            ... )
        """
        if seed is not None:
            np.random.seed(seed)
        
        if bounds is None:
            bounds = [(0, 1)]
        
        # Generate random samples
        n_dims = len(bounds)
        samples = np.zeros((n_samples, n_dims))
        
        for i, (low, high) in enumerate(bounds):
            samples[:, i] = np.random.uniform(low, high, n_samples)
        
        # Evaluate function
        if n_dims == 1:
            results = np.array([func(x[0]) for x in samples])
        else:
            results = np.array([func(x) for x in samples])
        
        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'samples': samples,
            'results': results
        }
    
    def finite_difference(self, func, x, h=1e-5, order=1):
        """
        Compute numerical derivative using finite differences.
        
        Args:
            func (callable): Function to differentiate
            x (float): Point at which to compute derivative
            h (float): Step size
            order (int): Order of derivative (1 or 2)
            
        Returns:
            float: Numerical derivative
            
        Example:
            >>> ne = NumericalExperimentation()
            >>> derivative = ne.finite_difference(lambda x: x**2, 2.0)
            >>> print(derivative)  # Should be close to 4.0
        """
        if order == 1:
            return (func(x + h) - func(x - h)) / (2 * h)
        elif order == 2:
            return (func(x + h) - 2*func(x) + func(x - h)) / (h**2)
        else:
            raise ValueError("Only order 1 and 2 derivatives are supported")
