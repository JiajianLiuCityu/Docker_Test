import matplotlib
matplotlib.use('TkAgg')  # Force usage of TkAgg backend for compatibility
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# 1. Configuration: Path Setup
# ==========================================
# Get the absolute path of the script directory (visualize folder)
#
script_dir = os.path.dirname(os.path.abspath(__file__))

#
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

results_dir = os.path.join(project_root, 'results', 'instances')

file_paths = {
    'c5.large (x86)': os.path.join(results_dir, 'c5.large.csv'),
    't3.micro (x86)': os.path.join(results_dir, 't3.micro.csv'),
    't4g.micro (ARM)': os.path.join(results_dir, 't4g.micro.csv')
}

# AWS Instance hourly pricing (Example data, update based on your actual billing/region)
price_data = {
    'c5.large (x86)': 0.085,  # $0.085/hr
    't3.micro (x86)': 0.0104,  # $0.0104/hr
    't4g.micro (ARM)': 0.0084  # $0.0084/hr
}

# ==========================================
# 2. Data Loading & Integration
# ==========================================
def load_data(paths):
    all_dfs = []
    for instance, path in paths.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['Instance'] = instance
            all_dfs.append(df)
        else:
            print(f"Warning: File not found at {path}")

    combined_df = pd.concat(all_dfs)
    # Pivot table: Metrics as rows, Instances as columns
    pivot_df = combined_df.pivot(index='Metric', columns='Instance', values='Value')
    return pivot_df

df_main = load_data(file_paths)

# ==========================================
# 3. Visualization Implementation
# ==========================================

# Set global style
plt.style.use('seaborn-v0_8-muted')
colors = ['#4c72b0', '#55a868', '#dd8452']  # Professional color scheme

# --- Chart 1: Core Compute & Memory Performance (Absolute Values) ---
def plot_absolute_performance(df):
    metrics = ['CPU_Throughput', 'Mem_Bandwidth']
    plot_df = df.loc[metrics]

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_df.plot(kind='bar', ax=ax, rot=0, color=colors)

    ax.set_title('Compute & Memory Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_ylabel('Performance Value (eps / MiB/s)')
    for container in ax.containers:
        ax.bar_label(container, padding=3, fmt='%.1f')

    plt.tight_layout()
    plt.savefig('abs_performance.png', dpi=300)
    plt.show()

# --- Chart 2: Normalized Performance (Baseline: t3.micro = 100%) ---
def plot_normalized_performance(df):
    # Use t3.micro (x86) as Baseline
    baseline = df['t3.micro (x86)']
    norm_df = df.div(baseline, axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    norm_df.plot(kind='barh', ax=ax, color=colors)

    ax.axvline(100, color='red', linestyle='--', alpha=0.5, label='Baseline (t3.micro)')
    ax.set_title('Normalized Performance Relative to t3.micro (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Performance Percentage (%)')
    ax.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig('norm_performance.png', dpi=300)
    plt.show()

# --- Chart 3: Cost-Efficiency Analysis (Price-Performance) ---
def plot_price_performance(df):
    # Calculate CPU throughput per dollar
    cpu_perf = df.loc['CPU_Throughput']
    prices = pd.Series(price_data)

    price_perf = cpu_perf / prices

    fig, ax = plt.subplots(figsize=(8, 6))
    price_perf.plot(kind='bar', ax=ax, color=colors, rot=0)

    ax.set_title('Cost-Efficiency: CPU Throughput per Dollar', fontsize=14, fontweight='bold')
    ax.set_ylabel('Throughput per $1 USD')

    for container in ax.containers:
        ax.bar_label(container, padding=3, fmt='%.0f')

    plt.tight_layout()
    plt.savefig('cost_efficiency.png', dpi=300)
    plt.show()

# ==========================================
# 4. Execution
# ==========================================
if not df_main.empty:
    plot_absolute_performance(df_main)
    plot_normalized_performance(df_main)
    plot_price_performance(df_main)
    print("All visualization charts have been generated and saved as PNG files.")