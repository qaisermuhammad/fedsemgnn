#!/usr/bin/env python3
"""
Generate specialized FedSemGNN analysis graphs for paper
Focus on FedSemGNN's unique features and advantages
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
from pathlib import Path

# Configure for publication quality
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 11,
    'figure.titlesize': 16,
    'savefig.dpi': 300,
    'figure.dpi': 300,
    'font.family': 'serif'
})

def create_fedsemgnn_advantage_analysis():
    """Create graphs highlighting FedSemGNN's advantages"""
    
    # Load data
    fedsemgnn = pd.read_csv('results/fedsemgnn_metrics.csv')
    flat_ppo = pd.read_csv('results/flat_fedppo_metrics.csv')
    hier_ppo = pd.read_csv('results/hier_fedppo_metrics.csv')
    hsqf = pd.read_csv('results/hsqf_metrics.csv')
    random = pd.read_csv('results/random_place_metrics.csv')
    
    # Create the analysis figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('FedSemGNN Performance Advantages Analysis', fontsize=18, fontweight='bold')
    
    colors = {
        'FedSemGNN': '#FF6B6B',
        'FlatFedPPO': '#4ECDC4', 
        'HierFedPPO': '#45B7D1',
        'HSQF': '#96CEB4',
        'RandomPlacement': '#FFEAA7'
    }
    
    # 1. Reward improvement over baselines
    ax1 = axes[0, 0]
    algorithms = ['FedSemGNN', 'FlatFedPPO', 'HierFedPPO', 'HSQF', 'RandomPlacement']
    data_frames = [fedsemgnn, flat_ppo, hier_ppo, hsqf, random]
    final_rewards = [df['Reward'].iloc[-100:].mean() for df in data_frames]  # Last 100 steps average
    
    bars = ax1.bar(algorithms, final_rewards, color=[colors[alg] for alg in algorithms])
    ax1.set_ylabel('Final Reward (System-wise, Last 100 Steps Avg)')
    ax1.set_title('Final Performance Comparison (System-wise, Last 100 Steps Avg)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add improvement percentages
    baseline_reward = final_rewards[4]  # RandomPlacement as baseline
    for i, (bar, reward) in enumerate(zip(bars, final_rewards)):
        if i > 0:  # Skip baseline
            improvement = ((reward - baseline_reward) / baseline_reward) * 100
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(final_rewards)*0.02,
                    f'+{improvement:.0f}%', ha='center', va='bottom', fontweight='bold')
        else:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(final_rewards)*0.02,
                    'Enhanced', ha='center', va='bottom', fontweight='bold', color='red')
    
    # 2. Semantic fidelity advantage
    ax2 = axes[0, 1]
    fidelities = [df['Fidelity_pct'].mean() for df in data_frames]
    bars = ax2.bar(algorithms, fidelities, color=[colors[alg] for alg in algorithms])
    ax2.set_ylabel('Average Semantic Fidelity (%) (System-wise)')
    ax2.set_title('Semantic Matching Performance (System-wise)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Highlight FedSemGNN
    bars[0].set_edgecolor('red')
    bars[0].set_linewidth(3)
    
    # 3. Convergence speed comparison
    ax3 = axes[0, 2]
    window = 50
    for i, (name, df) in enumerate(zip(algorithms, data_frames)):
        rewards_smooth = df['Reward'].rolling(window=window, min_periods=1).mean()
        ax3.plot(df['Step'], rewards_smooth, label=name, color=colors[name], 
                linewidth=3 if name == 'FedSemGNN' else 2,
                alpha=1.0 if name == 'FedSemGNN' else 0.7)
    
    ax3.set_xlabel('Simulation Step (Step-wise)')
    ax3.set_ylabel('Reward (Step-wise, Moving Average, window=50)')
    ax3.set_title('Convergence Speed Analysis (Step-wise, Moving Average)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Latency vs Performance trade-off
    ax4 = axes[1, 0]
    avg_latencies = [df['Latency_ms'].mean() for df in data_frames]
    avg_rewards = [df['Reward'].mean() for df in data_frames]
    
    for i, name in enumerate(algorithms):
        size = 200 if name == 'FedSemGNN' else 100
        ax4.scatter(avg_latencies[i], avg_rewards[i], color=colors[name], 
                   s=size, label=name, alpha=0.8, 
                   edgecolors='red' if name == 'FedSemGNN' else 'none',
                   linewidth=3 if name == 'FedSemGNN' else 0)
    
    ax4.set_xlabel('Average Latency (ms, System-wise)')
    ax4.set_ylabel('Average Reward (System-wise)')
    ax4.set_title('Latency vs Performance Trade-off (System-wise)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Communication efficiency
    ax5 = axes[1, 1]
    comm_efficiency = []
    for df in data_frames:
        if 'Bytes_cum_MB' in df.columns:
            final_bytes = df['Bytes_cum_MB'].iloc[-1] if df['Bytes_cum_MB'].iloc[-1] > 0 else 1
            final_reward = df['Reward'].iloc[-1]
            efficiency = final_reward / final_bytes
        else:
            efficiency = 0
        comm_efficiency.append(efficiency)
    
    bars = ax5.bar(algorithms, comm_efficiency, color=[colors[alg] for alg in algorithms])
    ax5.set_ylabel('Reward per MB Exchanged (System-wise)')
    ax5.set_title('Communication Efficiency (System-wise)')
    ax5.tick_params(axis='x', rotation=45)
    
    # Highlight FedSemGNN
    bars[0].set_edgecolor('red')
    bars[0].set_linewidth(3)
    
    # 6. Performance summary table
    ax6 = axes[1, 2]
    ax6.axis('tight')
    ax6.axis('off')
    
    # Create summary data
    summary_data = []
    metrics = ['Final Reward (System-wise, Last 100 Steps Avg)', 'Avg Latency (ms, System-wise)', 'Avg Fidelity (%) (System-wise)', 'Comm Efficiency (System-wise)']
    
    for i, name in enumerate(algorithms):
        row = [
            name,
            f"{final_rewards[i]:.0f}",
            f"{avg_latencies[i]:.2f}",
            f"{fidelities[i]:.1f}",
            f"{comm_efficiency[i]:.2f}"
        ]
        summary_data.append(row)
    
    table = ax6.table(cellText=summary_data,
                     colLabels=['Algorithm'] + metrics,
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Highlight FedSemGNN row
    for j in range(len(metrics) + 1):
        table[(1, j)].set_facecolor('#FFE5E5')  # Light red for FedSemGNN row
    
    ax6.set_title('Performance Summary Metrics')
    
    plt.tight_layout()
    plt.savefig('graphs/fedsemgnn_advantages.png', bbox_inches='tight')
    plt.savefig('graphs/fedsemgnn_advantages.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/fedsemgnn_advantages.png")

def create_scalability_demonstration():
    """Create graphs demonstrating scalability at 1000 steps"""
    
    # Load FedSemGNN data
    fedsemgnn = pd.read_csv('results/fedsemgnn_metrics.csv')
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('FedSemGNN Scalability at 1000 Steps', fontsize=16, fontweight='bold')
    
    # 1. Performance over time with confidence intervals
    ax1 = axes[0, 0]
    window = 100
    rewards = fedsemgnn['Reward'].rolling(window=window, min_periods=1).mean()
    rewards_std = fedsemgnn['Reward'].rolling(window=window, min_periods=1).std()
    
    ax1.plot(fedsemgnn['Step'], rewards, color='#FF6B6B', linewidth=2, label='Reward')
    ax1.fill_between(fedsemgnn['Step'], 
                     rewards - rewards_std, 
                     rewards + rewards_std, 
                     alpha=0.3, color='#FF6B6B', label='±1 Std Dev')
    
    ax1.set_xlabel('Simulation Step')
    ax1.set_ylabel('Reward')
    ax1.set_title('Performance Stability Over 1000 Steps')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Latency consistency
    ax2 = axes[0, 1]
    latency = fedsemgnn['Latency_ms'].rolling(window=window, min_periods=1).mean()
    latency_std = fedsemgnn['Latency_ms'].rolling(window=window, min_periods=1).std()
    
    ax2.plot(fedsemgnn['Step'], latency, color='#4ECDC4', linewidth=2, label='Latency')
    ax2.fill_between(fedsemgnn['Step'],
                     latency - latency_std,
                     latency + latency_std,
                     alpha=0.3, color='#4ECDC4', label='±1 Std Dev')
    
    ax2.set_xlabel('Simulation Step')
    ax2.set_ylabel('Latency (ms)')
    ax2.set_title('Latency Stability Over 1000 Steps')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Communication growth
    ax3 = axes[1, 0]
    if 'Bytes_cum_MB' in fedsemgnn.columns:
        ax3.plot(fedsemgnn['Step'], fedsemgnn['Bytes_cum_MB'], 
                color='#96CEB4', linewidth=2, label='Cumulative')
        
        if 'Bytes_step_MB' in fedsemgnn.columns:
            step_bytes = fedsemgnn['Bytes_step_MB'].rolling(window=50, min_periods=1).mean()
            ax3_twin = ax3.twinx()
            ax3_twin.plot(fedsemgnn['Step'], step_bytes, 
                         color='#FFEAA7', linewidth=2, linestyle='--', label='Per Step (MA)')
            ax3_twin.set_ylabel('Bytes per Step (MB)', color='#FFEAA7')
            ax3_twin.legend(loc='upper right')
    
    ax3.set_xlabel('Simulation Step')
    ax3.set_ylabel('Cumulative Bytes (MB)')
    ax3.set_title('Communication Overhead Growth')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # 4. Performance metrics distribution
    ax4 = axes[1, 1]
    
    # Create a violin plot of key metrics
    metrics_data = []
    labels = []
    
    # Normalize metrics for comparison
    reward_min = fedsemgnn['Reward'].min() if not fedsemgnn['Reward'].empty else 0
    reward_max = fedsemgnn['Reward'].max() if not fedsemgnn['Reward'].empty else 1
    reward_norm = (fedsemgnn['Reward'] - reward_min) / (reward_max - reward_min) if reward_max != reward_min else fedsemgnn['Reward']*0
    latency_min = fedsemgnn['Latency_ms'].min() if not fedsemgnn['Latency_ms'].empty else 0
    latency_max = fedsemgnn['Latency_ms'].max() if not fedsemgnn['Latency_ms'].empty else 1
    latency_norm = 1 - ((fedsemgnn['Latency_ms'] - latency_min) / (latency_max - latency_min)) if latency_max != latency_min else fedsemgnn['Latency_ms']*0
    fidelity_norm = fedsemgnn['Fidelity_pct'] / 100
    
    metrics_data = [reward_norm, latency_norm, fidelity_norm]
    labels = ['Reward\n(Normalized)', 'Latency\n(Inverted & Norm)', 'Fidelity\n(Normalized)']
    
    violin_parts = ax4.violinplot(metrics_data, positions=range(len(labels)), showmeans=True)
    ax4.set_xticks(range(len(labels)))
    ax4.set_xticklabels(labels)
    ax4.set_ylabel('Normalized Score (0-1)')
    ax4.set_title('Performance Metrics Distribution')
    ax4.grid(True, alpha=0.3)
    
    # Color the violins
    colors = ['#FF6B6B', '#4ECDC4', '#96CEB4']
    for i, pc in enumerate(violin_parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
    
    plt.tight_layout()
    plt.savefig('graphs/scalability_analysis/fedsemgnn_scalability_1000.png', bbox_inches='tight')
    plt.savefig('graphs/scalability_analysis/fedsemgnn_scalability_1000.pdf', bbox_inches='tight')
    plt.close()
    print("Created: graphs/fedsemgnn_scalability_1000.png")

def main():
    """Generate specialized FedSemGNN analysis graphs"""
    print("Generating specialized FedSemGNN analysis graphs...")
    
    # Ensure directories exist
    Path("graphs").mkdir(exist_ok=True)
    Path("graphs/scalability_analysis").mkdir(exist_ok=True)
    
    create_fedsemgnn_advantage_analysis()
    create_scalability_demonstration()
    
    print("\nSpecialized analysis graphs created!")
    print("Additional graphs:")
    print("   FedSemGNN Advantages: graphs/fedsemgnn_advantages.png")
    print("   Scalability Demo: graphs/scalability_analysis/fedsemgnn_scalability_1000.png")

if __name__ == "__main__":
    main()
