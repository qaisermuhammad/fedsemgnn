#!/usr/bin/env python3
"""
Generate individual metric graphs with professional scientific color schemes
Uses IEEE/Springer/Elsevier standard colors for top-tier journal publications
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
from pathlib import Path

# Configure for publication quality with scientific standards
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 16,
    'savefig.dpi': 300,
    'figure.dpi': 300,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'axes.linewidth': 1.2,
    'grid.linewidth': 0.8,
    'lines.linewidth': 2.0
})

# Create individual metrics directory
individual_dir = Path("graphs/individual_metrics_scientific")
individual_dir.mkdir(parents=True, exist_ok=True)

def get_scientific_colors():
    """Professional scientific color scheme for top-tier journals"""
    return {
        'FedSemGNN': '#1f77b4',        # Professional Blue (IEEE standard)
        'FlatFedPPO': '#ff7f0e',       # Professional Orange  
        'HierFedPPO': '#2ca02c',       # Professional Green
        'HSQF': '#d62728',             # Professional Red
        'RandomPlacement': '#9467bd'   # Professional Purple
    }

def get_scientific_markers():
    """Scientific marker styles for clarity"""
    return {
        'FedSemGNN': 'o',       # Circle
        'FlatFedPPO': 's',      # Square
        'HierFedPPO': '^',      # Triangle up
        'HSQF': 'D',            # Diamond
        'RandomPlacement': 'v'  # Triangle down
    }

def get_scientific_linestyles():
    """Scientific line styles for distinction"""
    return {
        'FedSemGNN': '-',       # Solid (our method)
        'FlatFedPPO': '--',     # Dashed
        'HierFedPPO': '-.',     # Dash-dot
        'HSQF': ':',            # Dotted
        'RandomPlacement': '--' # Dashed
    }

def load_all_metrics():
    """Load metrics from all algorithms"""
    algorithms = {
        'FedSemGNN': 'results/fedsemgnn_metrics.csv',
        'FlatFedPPO': 'results/flat_fedppo_metrics.csv', 
        'HierFedPPO': 'results/hier_fedppo_metrics.csv',
        'HSQF': 'results/hsqf_metrics.csv',
        'RandomPlacement': 'results/random_place_metrics.csv'
    }
    
    data = {}
    for name, file in algorithms.items():
        if os.path.exists(file):
            df = pd.read_csv(file)
            df['Algorithm'] = name
            data[name] = df
            print(f"Loaded {len(df)} steps from {name}")
        else:
            print(f"Missing: {file}")
    
    return data

def create_reward_comparison(data):
    """Individual graph: Reward over time for all strategies"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = get_scientific_colors()
    linestyles = get_scientific_linestyles()
    
    for name, df in data.items():
        # Smooth the reward curve with moving average
        window = 50
        rewards_smooth = df['Reward'].rolling(window=window, min_periods=1).mean()
        
        linewidth = 3 if name == 'FedSemGNN' else 2
        alpha = 1.0 if name == 'FedSemGNN' else 0.9
        
        ax.plot(df['Step'], rewards_smooth, 
               label=name, 
               color=colors[name], 
               linestyle=linestyles[name],
               linewidth=linewidth,
               alpha=alpha)
    
    ax.set_xlabel('Simulation Step (Step-wise)')
    ax.set_ylabel('Reward (Step-wise, Moving Average, window=50)')
    ax.set_title('Performance Comparison: Reward Over Time (Step-wise, Moving Average)')
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig = plt.gcf()
    fig.text(0.5, 0.96, 'Reward curves show step-wise moving averages (window=50).', ha='center', fontsize=11, color='gray')
    plt.savefig('graphs/individual_metrics_scientific/01_reward_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/01_reward_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/01_reward_comparison.png")

def create_latency_comparison(data):
    """Individual graph: Latency comparison for all strategies"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = get_scientific_colors()
    linestyles = get_scientific_linestyles()
    algorithms = list(data.keys())
    
    # Left plot: Average latency bar chart
    avg_latencies = [data[name]['Latency_ms'].mean() for name in algorithms]
    bars = ax1.bar(algorithms, avg_latencies, 
                   color=[colors[name] for name in algorithms],
                   alpha=0.8, edgecolor='black', linewidth=1)
    
    ax1.set_ylabel('Average Latency (ms, System-wise)')
    ax1.set_title('System-wise Average Latency Comparison')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Add value labels on bars
    for bar, latency in zip(bars, avg_latencies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_latencies)*0.01,
                f'{latency:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Right plot: Latency over time
    for name, df in data.items():
        window = 50
        latency_smooth = df['Latency_ms'].rolling(window=window, min_periods=1).mean()
        
        linewidth = 3 if name == 'FedSemGNN' else 2
        alpha = 1.0 if name == 'FedSemGNN' else 0.9
        
        ax2.plot(df['Step'], latency_smooth, 
                label=name, 
                color=colors[name], 
                linestyle=linestyles[name],
                linewidth=linewidth,
                alpha=alpha)
    
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Latency (ms)')
    ax2.set_title('Latency Stability Over Time')
    ax2.legend(frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/02_latency_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/02_latency_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/02_latency_comparison.png")

def create_fidelity_comparison(data):
    """Individual graph: Semantic fidelity comparison for all strategies"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = get_scientific_colors()
    linestyles = get_scientific_linestyles()
    algorithms = list(data.keys())
    
    # Left plot: Average fidelity bar chart
    avg_fidelities = [data[name]['Fidelity_pct'].mean() for name in algorithms]
    bars = ax1.bar(algorithms, avg_fidelities, 
                   color=[colors[name] for name in algorithms],
                   alpha=0.8, edgecolor='black', linewidth=1)
    
    ax1.set_ylabel('Average Semantic Fidelity (%)')
    ax1.set_title('Semantic Fidelity Comparison')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Highlight FedSemGNN with thicker border
    bars[0].set_edgecolor('black')
    bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, fidelity in zip(bars, avg_fidelities):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_fidelities)*0.01,
                f'{fidelity:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Right plot: Fidelity over time
    for name, df in data.items():
        window = 50
        fidelity_smooth = df['Fidelity_pct'].rolling(window=window, min_periods=1).mean()
        
        linewidth = 3 if name == 'FedSemGNN' else 2
        alpha = 1.0 if name == 'FedSemGNN' else 0.9
        
        ax2.plot(df['Step'], fidelity_smooth, 
                label=name, 
                color=colors[name], 
                linestyle=linestyles[name],
                linewidth=linewidth,
                alpha=alpha)
    
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Semantic Fidelity (%)')
    ax2.set_title('Semantic Fidelity Over Time')
    ax2.legend(frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/03_fidelity_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/03_fidelity_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/03_fidelity_comparison.png")

def create_power_comparison(data):
    """Individual graph: Power consumption comparison for all strategies"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = get_scientific_colors()
    algorithms = list(data.keys())
    
    # Calculate average power consumption
    avg_powers = []
    for name in algorithms:
        df = data[name]
        if 'Power_W' in df.columns:
            avg_power = df['Power_W'].mean()
        else:
            avg_power = 0  # No power data available
        avg_powers.append(avg_power)
    
    bars = ax.bar(algorithms, avg_powers, 
                  color=[colors[name] for name in algorithms],
                  alpha=0.8, edgecolor='black', linewidth=1)
    
    ax.set_ylabel('Average Power Consumption (W)')
    ax.set_title('Power Consumption Comparison')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Highlight FedSemGNN
    if avg_powers[0] > 0:
        bars[0].set_edgecolor('black')
        bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, power in zip(bars, avg_powers):
        if power > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_powers)*0.01,
                   f'{power:.0f}W', ha='center', va='bottom', fontweight='bold', fontsize=10)
        else:
            ax.text(bar.get_x() + bar.get_width()/2, 5,
                   'N/A', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/04_power_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/04_power_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/04_power_comparison.png")

def create_communication_comparison(data):
    """Individual graph: Communication overhead comparison for all strategies"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = get_scientific_colors()
    linestyles = get_scientific_linestyles()
    algorithms = list(data.keys())
    
    # Left plot: Total communication overhead
    total_comms = []
    for name in algorithms:
        df = data[name]
        if 'Bytes_cum_MB' in df.columns and len(df) > 0:
            total_comm = df['Bytes_cum_MB'].iloc[-1]
        else:
            total_comm = 0
        total_comms.append(total_comm)
    
    bars = ax1.bar(algorithms, total_comms, 
                   color=[colors[name] for name in algorithms],
                   alpha=0.8, edgecolor='black', linewidth=1)
    
    ax1.set_ylabel('Total Communication (MB)')
    ax1.set_title('Total Communication Overhead')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Add value labels on bars
    for bar, comm in zip(bars, total_comms):
        if comm > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_comms)*0.01,
                    f'{comm:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        else:
            ax1.text(bar.get_x() + bar.get_width()/2, 0.5,
                    'N/A', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Right plot: Communication over time
    for name, df in data.items():
        if 'Bytes_cum_MB' in df.columns:
            linewidth = 3 if name == 'FedSemGNN' else 2
            alpha = 1.0 if name == 'FedSemGNN' else 0.9
            
            ax2.plot(df['Step'], df['Bytes_cum_MB'], 
                    label=name, 
                    color=colors[name], 
                    linestyle=linestyles[name],
                    linewidth=linewidth,
                    alpha=alpha)
    
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Cumulative Communication (MB)')
    ax2.set_title('Communication Growth Over Time')
    ax2.legend(frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/05_communication_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/05_communication_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/05_communication_comparison.png")

def create_efficiency_comparison(data):
    """Individual graph: Algorithm efficiency comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = get_scientific_colors()
    algorithms = list(data.keys())
    
    # Calculate efficiency as final reward per step
    efficiencies = []
    for name in algorithms:
        df = data[name]
        final_reward = df['Reward'].iloc[-100:].mean()  # Average of last 100 steps
        total_steps = len(df)
        efficiency = final_reward / total_steps if total_steps > 0 else 0
        efficiencies.append(efficiency)
    
    bars = ax.bar(algorithms, efficiencies, 
                  color=[colors[name] for name in algorithms],
                  alpha=0.8, edgecolor='black', linewidth=1)
    
    ax.set_ylabel('Efficiency (Reward per Step)')
    ax.set_title('Algorithm Efficiency Comparison')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Highlight FedSemGNN
    bars[0].set_edgecolor('black')
    bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, eff in zip(bars, efficiencies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(efficiencies)*0.01,
               f'{eff:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/06_efficiency_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/06_efficiency_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/06_efficiency_comparison.png")

def create_convergence_comparison(data):
    """Individual graph: Convergence speed comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = get_scientific_colors()
    linestyles = get_scientific_linestyles()
    
    for name, df in data.items():
        # Calculate cumulative maximum reward (convergence indicator)
        cumulative_max = df['Reward'].expanding().max()
        
        linewidth = 3 if name == 'FedSemGNN' else 2
        alpha = 1.0 if name == 'FedSemGNN' else 0.9
        
        ax.plot(df['Step'], cumulative_max, 
               label=name, 
               color=colors[name], 
               linestyle=linestyles[name],
               linewidth=linewidth,
               alpha=alpha)
    
    ax2.set_xlabel('Simulation Step (Step-wise)')
    ax2.set_ylabel('Latency (Step-wise, Moving Average, window=50)')
    ax2.set_title('Latency Stability Over Time (Step-wise, Moving Average)')
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/07_convergence_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/07_convergence_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/07_convergence_comparison.png")

def create_stability_comparison(data):
    """Individual graph: Performance stability comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = get_scientific_colors()
    algorithms = list(data.keys())
    
    # Calculate stability metrics (coefficient of variation - lower is better)
    stability_scores = []
    for name in algorithms:
        df = data[name]
        # Calculate coefficient of variation for reward (lower = more stable)
        reward_cv = df['Reward'].std() / df['Reward'].mean() if df['Reward'].mean() > 0 else 0
        # Invert so higher score = more stable
        stability = 1 / (1 + reward_cv)
        stability_scores.append(stability)
    
    bars = ax.bar(algorithms, stability_scores, 
                  color=[colors[name] for name in algorithms],
                  alpha=0.8, edgecolor='black', linewidth=1)
    
    ax.set_ylabel('Stability Score (Higher = More Stable)')
    ax.set_title('Performance Stability Comparison')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Highlight FedSemGNN
    bars[0].set_edgecolor('black')
    bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, stability in zip(bars, stability_scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(stability_scores)*0.01,
               f'{stability:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('graphs/individual_metrics_scientific/08_stability_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/individual_metrics_scientific/08_stability_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/individual_metrics_scientific/08_stability_comparison.png")

def main():
    """Generate all individual metric graphs with scientific color schemes"""
    print("Generating individual metric graphs with scientific color schemes...")
    print("Using IEEE/Springer/Elsevier standard colors for top-tier publications")
    
    # Load all data
    data = load_all_metrics()
    
    if len(data) < 2:
        print("Need at least 2 algorithms to create comparisons")
        return
    
    # Generate individual metric graphs
    print("\nCreating individual metric graphs with professional colors...")
    create_reward_comparison(data)
    create_latency_comparison(data)
    create_fidelity_comparison(data)
    create_power_comparison(data)
    create_communication_comparison(data)
    create_efficiency_comparison(data)
    create_convergence_comparison(data)
    create_stability_comparison(data)
    
    print(f"\nAll scientific-grade individual metric graphs generated!")
    print(f"Location: {Path('graphs/individual_metrics_scientific').absolute()}")
    print(f"Total: 16 files (8 PNG + 8 PDF)")
    print(f"\nProfessional Scientific Colors Used:")
    colors = get_scientific_colors()
    for alg, color in colors.items():
        print(f"   {alg}: {color}")
    print(f"\nReady for submission to top-tier journals!")

if __name__ == "__main__":
    main()