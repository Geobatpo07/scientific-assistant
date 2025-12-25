"""
Example 3: Data Science and Visualization
==========================================

This example demonstrates data science capabilities including data exploration,
cleaning, visualization, and statistical analysis.
"""

from scientific_assistant import ScientificAssistant
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialize the assistant
assistant = ScientificAssistant()

print("=" * 60)
print("EXAMPLE 3: DATA SCIENCE AND VISUALIZATION")
print("=" * 60)

# Create a sample dataset
print("\n1. Creating Sample Dataset")
print("-" * 40)

np.random.seed(42)
n_samples = 100

df = pd.DataFrame({
    'age': np.random.randint(20, 70, n_samples),
    'income': np.random.normal(50000, 15000, n_samples),
    'education_years': np.random.randint(10, 20, n_samples),
    'satisfaction': np.random.randint(1, 11, n_samples)
})

# Add some missing values
df.loc[5:7, 'income'] = np.nan
df.loc[10:12, 'satisfaction'] = np.nan

print(f"Created dataset with {n_samples} samples and {len(df.columns)} features")

# 2. Data Exploration
print("\n2. Data Exploration")
print("-" * 40)

info = assistant.data.load_and_explore(df)
print(f"Dataset shape: {info['shape']}")
print(f"Columns: {info['columns']}")
print(f"\nMissing values:")
for col, missing in info['missing_values'].items():
    if missing > 0:
        print(f"  {col}: {missing} missing")

print(f"\nBasic statistics:")
print(info['description'])

# 3. Data Cleaning
print("\n3. Data Cleaning")
print("-" * 40)

# Clean the data by filling missing values with mean
df_clean = assistant.data.clean_data(df, fill_na_method='mean')
print(f"Original dataset: {df.shape[0]} rows")
print(f"Cleaned dataset: {df_clean.shape[0]} rows")
print(f"Missing values after cleaning: {df_clean.isnull().sum().sum()}")

# 4. Summary Statistics
print("\n4. Summary Statistics")
print("-" * 40)

stats = assistant.data.summary_statistics(df_clean, 'income')
print("Income statistics:")
print(f"  Mean: ${stats['mean']:.2f}")
print(f"  Median: ${stats['median']:.2f}")
print(f"  Std Dev: ${stats['std']:.2f}")
print(f"  Min: ${stats['min']:.2f}")
print(f"  Max: ${stats['max']:.2f}")
print(f"  Skewness: {stats['skewness']:.4f}")
print(f"  Kurtosis: {stats['kurtosis']:.4f}")

# 5. Correlation Analysis
print("\n5. Correlation Analysis")
print("-" * 40)

corr_result = assistant.data.correlation_analysis(df_clean, method='pearson', plot=False)
print("Correlation matrix:")
print(corr_result['correlation_matrix'])

# 6. Group Analysis
print("\n6. Group Analysis")
print("-" * 40)

# Group by age ranges
df_clean['age_group'] = pd.cut(df_clean['age'], bins=[0, 30, 50, 100], labels=['Young', 'Middle', 'Senior'])
grouped = assistant.data.group_analysis(df_clean, 'age_group', 'income', 'mean')
print("Average income by age group:")
print(grouped)

# 7. Visualization Example (commented out to avoid display issues)
print("\n7. Visualization (creating plots)")
print("-" * 40)

# Create distribution plot
fig1 = assistant.data.visualize_distribution(df_clean, 'income', plot_type='histogram', bins=20)
fig1.suptitle('Income Distribution')
plt.savefig('/tmp/income_distribution.png', dpi=100, bbox_inches='tight')
plt.close(fig1)
print("✓ Saved income distribution plot to /tmp/income_distribution.png")

# Create correlation heatmap
corr_result = assistant.data.correlation_analysis(df_clean, method='pearson', plot=True)
if 'figure' in corr_result:
    plt.savefig('/tmp/correlation_heatmap.png', dpi=100, bbox_inches='tight')
    plt.close(corr_result['figure'])
    print("✓ Saved correlation heatmap to /tmp/correlation_heatmap.png")

# Create time series plot (using age as pseudo-time)
df_clean_sorted = df_clean.sort_values('age').reset_index(drop=True)
fig3 = assistant.data.time_series_plot(df_clean_sorted['income'].values, title='Income vs Age Order')
plt.savefig('/tmp/income_timeseries.png', dpi=100, bbox_inches='tight')
plt.close(fig3)
print("✓ Saved time series plot to /tmp/income_timeseries.png")

print("\n" + "=" * 60)
print("Example complete!")
print("=" * 60)
