#!/usr/bin/env python3
"""
Generate individual metric graphs for FedSemGNN paper
Each metric gets its own high-quality graph with all 5 strategies side by side
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
from pathlib import Path

# Configure for publication quality
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.titlesize': 18,
    'savefig.dpi': 300,
    'figure.dpi': 300,
    'font.family': 'serif'
})

graphs_dir = Path("graphs")
graphs_dir.mkdir(exist_ok=True)

def load_all_metrics():
    """Load metrics from all algorithms"""
    algorithms = {
        'FedSemGNN': 'results/fedsemgnn_metrics.csv',
        'FlatFedPPO': 'results/flatfedppo_metrics.csv',
        'HierFedPPO': 'results/hierfedppo_metrics.csv',
        'HSQF': 'results/hsqf_metrics.csv',
        'RandomPlacement': 'results/randomplacement_metrics.csv'
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
    plt.figure(figsize=(12, 8))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    for name, df in data.items():
        # Smooth the reward curve with moving average
        window = 50
        rewards_smooth = df['Reward'].rolling(window=window, min_periods=1).mean()
        plt.plot(df['Step'], rewards_smooth, label=name, color=colors[name], 
                linewidth=3 if name == 'FedSemGNN' else 2,
                alpha=1.0 if name == 'FedSemGNN' else 0.8)
    
    plt.xlabel('Simulation Step (Step-wise)')
    plt.ylabel('Reward (Step-wise, Moving Average, window=50)')
    plt.title('Reward Performance Comparison Across All Strategies (Step-wise, Moving Average)')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.figtext(0.5, 0.01, 'Reward curves show step-wise moving averages (window=50).', ha='center', fontsize=11, color='gray')
    plt.savefig('graphs/01_reward_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/01_reward_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/01_reward_comparison.png")

def create_latency_comparison(data):
    """Individual graph: Latency comparison for all strategies"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    algorithms = list(data.keys())
    
    # Left plot: Average latency bar chart
    avg_latencies = [data[name]['Latency_ms'].mean() for name in algorithms]
    bars = ax1.bar(algorithms, avg_latencies, color=[colors[name] for name in algorithms])
    ax1.set_ylabel('Average Latency (ms, System-wise)')
    ax1.set_title('System-wise Average Latency Comparison')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, latency in zip(bars, avg_latencies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_latencies)*0.01,
                f'{latency:.2f}ms', ha='center', va='bottom', fontweight='bold')
    
    # Right plot: Latency over time
    for name, df in data.items():
        window = 50
        latency_smooth = df['Latency_ms'].rolling(window=window, min_periods=1).mean()
        ax2.plot(df['Step'], latency_smooth, label=name, color=colors[name], 
                linewidth=3 if name == 'FedSemGNN' else 2,
                alpha=1.0 if name == 'FedSemGNN' else 0.8)
    
    ax2.set_xlabel('Simulation Step (Step-wise)')
    ax2.set_ylabel('Latency (Step-wise, Moving Average, window=50)')
    ax2.set_title('Latency Stability Over Time (Step-wise, Moving Average)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig = plt.gcf()
    fig.text(0.5, 0.96, 'Left: System-wise average latency. Right: Step-wise moving average (window=50).', ha='center', fontsize=11, color='gray')
    plt.savefig('graphs/02_latency_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/02_latency_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/02_latency_comparison.png")

def create_fidelity_comparison(data):
    """Individual graph: Semantic fidelity comparison for all strategies"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    algorithms = list(data.keys())
    
    # Left plot: Average fidelity bar chart
    avg_fidelities = [data[name]['Fidelity_pct'].mean() for name in algorithms]
    bars = ax1.bar(algorithms, avg_fidelities, color=[colors[name] for name in algorithms])
    ax1.set_ylabel('Average Semantic Fidelity (%) (System-wise)')
    ax1.set_title('System-wise Semantic Fidelity Comparison')
    ax1.tick_params(axis='x', rotation=45)
    
    # Highlight FedSemGNN
    bars[0].set_edgecolor('darkred')
    bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, fidelity in zip(bars, avg_fidelities):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_fidelities)*0.01,
                f'{fidelity:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Right plot: Fidelity over time
    for name, df in data.items():
        window = 50
        fidelity_smooth = df['Fidelity_pct'].rolling(window=window, min_periods=1).mean()
        ax2.plot(df['Step'], fidelity_smooth, label=name, color=colors[name], 
                linewidth=3 if name == 'FedSemGNN' else 2,
                alpha=1.0 if name == 'FedSemGNN' else 0.8)
    
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Semantic Fidelity (%, Moving Average)')
    ax2.set_title('Semantic Fidelity Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graphs/03_fidelity_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/03_fidelity_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/03_fidelity_comparison.png")

def create_power_comparison(data):
    """Individual graph: Power consumption comparison for all strategies"""
    plt.figure(figsize=(12, 8))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
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
    
    bars = plt.bar(algorithms, avg_powers, color=[colors[name] for name in algorithms])
    plt.ylabel('Average Power Consumption (W)')
    plt.title('Power Consumption Comparison Across All Strategies')
    plt.xticks(rotation=45)
    
    # Highlight FedSemGNN
    if avg_powers[0] > 0:
        bars[0].set_edgecolor('darkred')
        bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, power in zip(bars, avg_powers):
        if power > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_powers)*0.01,
                    f'{power:.0f}W', ha='center', va='bottom', fontweight='bold')
        else:
            plt.text(bar.get_x() + bar.get_width()/2, 10,
                    'N/A', ha='center', va='bottom', fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('graphs/04_power_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/04_power_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/04_power_comparison.png")

def create_communication_comparison(data):
    """Individual graph: Communication overhead comparison for all strategies"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
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
    
    bars = ax1.bar(algorithms, total_comms, color=[colors[name] for name in algorithms])
    ax1.set_ylabel('Total Communication (MB)')
    ax1.set_title('Total Communication Overhead')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, comm in zip(bars, total_comms):
        if comm > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_comms)*0.01,
                    f'{comm:.1f}MB', ha='center', va='bottom', fontweight='bold')
        else:
            ax1.text(bar.get_x() + bar.get_width()/2, 1,
                    'N/A', ha='center', va='bottom', fontweight='bold')
    
    # Right plot: Communication over time
    for name, df in data.items():
        if 'Bytes_cum_MB' in df.columns:
            ax2.plot(df['Step'], df['Bytes_cum_MB'], label=name, color=colors[name], 
                    linewidth=3 if name == 'FedSemGNN' else 2,
                    alpha=1.0 if name == 'FedSemGNN' else 0.8)
    
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Cumulative Communication (MB)')
    ax2.set_title('Communication Growth Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graphs/05_communication_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/05_communication_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/05_communication_comparison.png")

def create_efficiency_comparison(data):
    """Individual graph: Algorithm efficiency comparison"""
    plt.figure(figsize=(12, 8))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    algorithms = list(data.keys())
    
    # Calculate efficiency as final reward per step
    efficiencies = []
    for name in algorithms:
        df = data[name]
        final_reward = df['Reward'].iloc[-100:].mean()  # Average of last 100 steps
        total_steps = len(df)
        efficiency = final_reward / total_steps if total_steps > 0 else 0
        efficiencies.append(efficiency)
    
    bars = plt.bar(algorithms, efficiencies, color=[colors[name] for name in algorithms])
    plt.ylabel('Efficiency (Reward per Step)')
    plt.title('Algorithm Efficiency Comparison')
    plt.xticks(rotation=45)
    
    # Highlight FedSemGNN
    bars[0].set_edgecolor('darkred')
    bars[0].set_linewidth(3)
    
    # Add value labels on bars
    for bar, eff in zip(bars, efficiencies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(efficiencies)*0.01,
                f'{eff:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('graphs/06_efficiency_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/06_efficiency_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/06_efficiency_comparison.png")

def create_convergence_comparison(data):
    """Individual graph: Convergence speed comparison"""
    plt.figure(figsize=(12, 8))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    for name, df in data.items():
        # Calculate cumulative maximum reward (convergence indicator)
        cumulative_max = df['Reward'].expanding().max()
        plt.plot(df['Step'], cumulative_max, label=name, color=colors[name], 
                linewidth=3 if name == 'FedSemGNN' else 2,
                alpha=1.0 if name == 'FedSemGNN' else 0.8)
    
    plt.xlabel('Simulation Step')
    plt.ylabel('Cumulative Maximum Reward')
    plt.title('Convergence Speed Comparison (Cumulative Best Performance)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('graphs/07_convergence_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/07_convergence_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/07_convergence_comparison.png")

def create_stability_comparison(data):
    """Individual graph: Performance stability comparison"""
    plt.figure(figsize=(12, 8))
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    algorithms = list(data.keys())
    
    # Calculate stability metrics
    reward_stds = [data[name]['Reward'].std() for name in algorithms]
    latency_stds = [data[name]['Latency_ms'].std() for name in algorithms]
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, reward_stds, width, label='Reward Std Dev', 
                   color=[colors[name] for name in algorithms], alpha=0.8)
    
    # Create secondary y-axis for latency
    ax2 = plt.gca().twinx()
    bars2 = ax2.bar(x + width/2, latency_stds, width, label='Latency Std Dev', 
                   color=[colors[name] for name in algorithms], alpha=0.6)
    
    plt.gca().set_xlabel('Algorithm')
    plt.gca().set_ylabel('Reward Standard Deviation', color='black')
    ax2.set_ylabel('Latency Standard Deviation (ms)', color='gray')
    plt.gca().set_title('Performance Stability Comparison')
    plt.gca().set_xticks(x)
    plt.gca().set_xticklabels(algorithms, rotation=45)
    
    # Add legends
    plt.gca().legend(loc='upper left')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('graphs/08_stability_comparison.png', bbox_inches='tight')
    plt.savefig('graphs/08_stability_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/08_stability_comparison.png")

def main():
    """Generate all individual metric graphs"""
    print("Generating individual metric graphs for paper...")
    
    # Load all data
    data = load_all_metrics()
    
    if len(data) < 2:
        print("Need at least 2 algorithms to create comparisons")
        return
    
    # Generate individual metric graphs
    print("\nCreating individual metric graphs...")
    create_reward_comparison(data)
    create_latency_comparison(data)
    create_fidelity_comparison(data)
    create_power_comparison(data)
    create_communication_comparison(data)
    create_efficiency_comparison(data)
    create_convergence_comparison(data)
    create_stability_comparison(data)
    
    print(f"\nAll individual metric graphs generated!")
    print(f"Location: {Path('graphs').absolute()}")
    print(f"Total: 16 files (8 PNG + 8 PDF)")
    print(f"\nIndividual Metrics Available:")
    print(f"   01. Reward Comparison")
    print(f"   02. Latency Comparison")
    print(f"   03. Semantic Fidelity Comparison")
    print(f"   04. Power Consumption Comparison")
    print(f"   05. Communication Overhead Comparison")
    print(f"   06. Algorithm Efficiency Comparison")
    print(f"   07. Convergence Speed Comparison")
    print(f"   08. Performance Stability Comparison")

if __name__ == "__main__":
    main()