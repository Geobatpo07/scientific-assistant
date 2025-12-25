"""Data science tools for data processing, visualization, and analysis."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional


class DataScienceTools:
    """
    Tools for data science including:
    - Data loading and exploration
    - Data cleaning and preprocessing
    - Visualization
    - Statistical analysis
    """
    
    def __init__(self):
        """Initialize data science tools."""
        sns.set_style("whitegrid")
    
    def load_and_explore(self, data, head_rows=5):
        """
        Load and explore a dataset.
        
        Args:
            data (str or DataFrame): Path to CSV file or DataFrame
            head_rows (int): Number of rows to display
            
        Returns:
            dict: Dataset information and statistics
            
        Example:
            >>> ds = DataScienceTools()
            >>> info = ds.load_and_explore("data.csv")
        """
        if isinstance(data, str):
            df = pd.read_csv(data)
        else:
            df = data
        
        return {
            'dataframe': df,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'head': df.head(head_rows),
            'description': df.describe(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
    
    def clean_data(self, df, drop_duplicates=True, drop_na=False, fill_na_method=None):
        """
        Clean a dataset.
        
        Args:
            df (DataFrame): Input dataframe
            drop_duplicates (bool): Whether to drop duplicate rows
            drop_na (bool): Whether to drop rows with missing values
            fill_na_method (str, optional): Method to fill NAs ('mean', 'median', 'mode', 'forward', 'backward')
            
        Returns:
            DataFrame: Cleaned dataframe
            
        Example:
            >>> ds = DataScienceTools()
            >>> clean_df = ds.clean_data(df, fill_na_method='mean')
        """
        df_clean = df.copy()
        
        if drop_duplicates:
            df_clean = df_clean.drop_duplicates()
        
        if drop_na:
            df_clean = df_clean.dropna()
        elif fill_na_method:
            if fill_na_method == 'mean':
                df_clean = df_clean.fillna(df_clean.mean(numeric_only=True))
            elif fill_na_method == 'median':
                df_clean = df_clean.fillna(df_clean.median(numeric_only=True))
            elif fill_na_method == 'mode':
                df_clean = df_clean.fillna(df_clean.mode().iloc[0])
            elif fill_na_method == 'forward':
                df_clean = df_clean.ffill()
            elif fill_na_method == 'backward':
                df_clean = df_clean.bfill()
        
        return df_clean
    
    def visualize_distribution(self, data, column=None, plot_type='histogram', bins=30):
        """
        Visualize data distribution.
        
        Args:
            data (DataFrame or array-like): Data to visualize
            column (str, optional): Column name if data is DataFrame
            plot_type (str): Type of plot ('histogram', 'density', 'box')
            bins (int): Number of bins for histogram
            
        Returns:
            matplotlib.figure.Figure: The figure object
            
        Example:
            >>> ds = DataScienceTools()
            >>> fig = ds.visualize_distribution(df, column='age', plot_type='histogram')
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if isinstance(data, pd.DataFrame) and column:
            plot_data = data[column]
        else:
            plot_data = data
        
        if plot_type == 'histogram':
            ax.hist(plot_data, bins=bins, edgecolor='black', alpha=0.7)
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution (Histogram)')
        elif plot_type == 'density':
            plot_data.plot(kind='density', ax=ax)
            ax.set_xlabel('Value')
            ax.set_ylabel('Density')
            ax.set_title('Distribution (Density)')
        elif plot_type == 'box':
            ax.boxplot(plot_data)
            ax.set_ylabel('Value')
            ax.set_title('Distribution (Box Plot)')
        
        plt.tight_layout()
        return fig
    
    def correlation_analysis(self, df, method='pearson', plot=True):
        """
        Perform correlation analysis.
        
        Args:
            df (DataFrame): Input dataframe
            method (str): Correlation method ('pearson', 'spearman', 'kendall')
            plot (bool): Whether to plot correlation heatmap
            
        Returns:
            dict: Correlation matrix and optionally a figure
            
        Example:
            >>> ds = DataScienceTools()
            >>> result = ds.correlation_analysis(df, method='pearson')
        """
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr(method=method)
        
        result = {'correlation_matrix': corr_matrix}
        
        if plot:
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, linewidths=1, ax=ax, fmt='.2f')
            ax.set_title(f'Correlation Matrix ({method.capitalize()})')
            plt.tight_layout()
            result['figure'] = fig
        
        return result
    
    def time_series_plot(self, data, time_column=None, value_column=None, title='Time Series'):
        """
        Create a time series plot.
        
        Args:
            data (DataFrame or array-like): Time series data
            time_column (str, optional): Name of time column
            value_column (str, optional): Name of value column
            title (str): Plot title
            
        Returns:
            matplotlib.figure.Figure: The figure object
            
        Example:
            >>> ds = DataScienceTools()
            >>> fig = ds.time_series_plot(df, time_column='date', value_column='value')
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if isinstance(data, pd.DataFrame):
            if time_column and value_column:
                ax.plot(data[time_column], data[value_column])
            else:
                data.plot(ax=ax)
        else:
            ax.plot(data)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig
    
    def summary_statistics(self, data, column=None):
        """
        Calculate comprehensive summary statistics.
        
        Args:
            data (DataFrame or array-like): Data to analyze
            column (str, optional): Column name if data is DataFrame
            
        Returns:
            dict: Summary statistics
            
        Example:
            >>> ds = DataScienceTools()
            >>> stats = ds.summary_statistics(df, column='age')
        """
        if isinstance(data, pd.DataFrame) and column:
            series = data[column]
        elif isinstance(data, pd.DataFrame):
            return {col: self.summary_statistics(data[col]) 
                   for col in data.select_dtypes(include=[np.number]).columns}
        else:
            series = pd.Series(data)
        
        return {
            'count': len(series),
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max(),
            'q25': series.quantile(0.25),
            'q75': series.quantile(0.75),
            'skewness': series.skew(),
            'kurtosis': series.kurtosis()
        }
    
    def group_analysis(self, df, group_by, agg_column, agg_func='mean'):
        """
        Perform group-by analysis.
        
        Args:
            df (DataFrame): Input dataframe
            group_by (str or list): Column(s) to group by
            agg_column (str): Column to aggregate
            agg_func (str or list): Aggregation function(s)
            
        Returns:
            DataFrame: Grouped and aggregated data
            
        Example:
            >>> ds = DataScienceTools()
            >>> result = ds.group_analysis(df, 'category', 'value', 'mean')
        """
        return df.groupby(group_by)[agg_column].agg(agg_func)
