"""Statistical and machine learning modeling tools."""

import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA


class ModelingTools:
    """
    Tools for statistical and machine learning modeling including:
    - Linear and logistic regression
    - Random forests
    - Time series analysis
    - Model evaluation
    """
    
    def __init__(self):
        """Initialize modeling tools."""
        self.scaler = StandardScaler()
    
    def linear_regression(self, X, y, fit_intercept=True, return_metrics=True):
        """
        Fit a linear regression model.
        
        Args:
            X (array-like): Features
            y (array-like): Target variable
            fit_intercept (bool): Whether to fit intercept
            return_metrics (bool): Whether to return metrics
            
        Returns:
            dict: Model and metrics if return_metrics=True, else just model
            
        Example:
            >>> mt = ModelingTools()
            >>> X = [[1], [2], [3], [4]]
            >>> y = [2, 4, 6, 8]
            >>> result = mt.linear_regression(X, y)
        """
        model = LinearRegression(fit_intercept=fit_intercept)
        model.fit(X, y)
        
        if return_metrics:
            y_pred = model.predict(X)
            r2 = model.score(X, y)
            
            return {
                'model': model,
                'coefficients': model.coef_,
                'intercept': model.intercept_,
                'r2_score': r2,
                'predictions': y_pred
            }
        
        return model
    
    def logistic_regression(self, X, y, test_size=0.2, random_state=42):
        """
        Fit a logistic regression model for classification.
        
        Args:
            X (array-like): Features
            y (array-like): Target labels
            test_size (float): Proportion of test set
            random_state (int): Random seed
            
        Returns:
            dict: Model and evaluation metrics
            
        Example:
            >>> mt = ModelingTools()
            >>> X = [[1, 2], [2, 3], [3, 4], [4, 5]]
            >>> y = [0, 0, 1, 1]
            >>> result = mt.logistic_regression(X, y)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        model = LogisticRegression()
        model.fit(X_train, y_train)
        
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        return {
            'model': model,
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'coefficients': model.coef_,
            'intercept': model.intercept_
        }
    
    def random_forest(self, X, y, task='classification', n_estimators=100, 
                     test_size=0.2, random_state=42):
        """
        Fit a random forest model.
        
        Args:
            X (array-like): Features
            y (array-like): Target variable
            task (str): 'classification' or 'regression'
            n_estimators (int): Number of trees
            test_size (float): Proportion of test set
            random_state (int): Random seed
            
        Returns:
            dict: Model and evaluation metrics
            
        Example:
            >>> mt = ModelingTools()
            >>> X = [[1, 2], [2, 3], [3, 4], [4, 5]]
            >>> y = [0, 0, 1, 1]
            >>> result = mt.random_forest(X, y, task='classification')
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        if task == 'classification':
            model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        else:
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        
        model.fit(X_train, y_train)
        
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        return {
            'model': model,
            'train_score': train_score,
            'test_score': test_score,
            'feature_importance': model.feature_importances_
        }
    
    def time_series_arima(self, data, order=(1, 1, 1)):
        """
        Fit an ARIMA time series model.
        
        Args:
            data (array-like): Time series data
            order (tuple): ARIMA order (p, d, q)
            
        Returns:
            dict: Model and results
            
        Example:
            >>> mt = ModelingTools()
            >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            >>> result = mt.time_series_arima(data, order=(1, 1, 1))
        """
        model = ARIMA(data, order=order)
        fitted_model = model.fit()
        
        return {
            'model': fitted_model,
            'aic': fitted_model.aic,
            'bic': fitted_model.bic,
            'summary': fitted_model.summary()
        }
    
    def ols_regression(self, X, y):
        """
        Perform Ordinary Least Squares regression using statsmodels.
        
        Args:
            X (array-like): Features
            y (array-like): Target variable
            
        Returns:
            statsmodels.regression.linear_model.RegressionResultsWrapper: OLS results
            
        Example:
            >>> mt = ModelingTools()
            >>> X = [[1], [2], [3], [4]]
            >>> y = [2, 4, 6, 8]
            >>> result = mt.ols_regression(X, y)
            >>> print(result.summary())
        """
        X = sm.add_constant(X)
        model = sm.OLS(y, X)
        results = model.fit()
        
        return results
    
    def cross_validate(self, model, X, y, cv=5):
        """
        Perform cross-validation on a model.
        
        Args:
            model: sklearn model
            X (array-like): Features
            y (array-like): Target variable
            cv (int): Number of folds
            
        Returns:
            dict: Cross-validation scores
            
        Example:
            >>> from sklearn.linear_model import LinearRegression
            >>> mt = ModelingTools()
            >>> model = LinearRegression()
            >>> X = [[1], [2], [3], [4], [5]]
            >>> y = [2, 4, 6, 8, 10]
            >>> result = mt.cross_validate(model, X, y)
        """
        scores = cross_val_score(model, X, y, cv=cv)
        
        return {
            'scores': scores,
            'mean_score': scores.mean(),
            'std_score': scores.std()
        }
