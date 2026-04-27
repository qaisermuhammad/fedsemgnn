#plot_cluster_rewards.py

import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Handle metrics logger import with fallback
try:
    from visualizations.metrics.metrics_logger import load_json_trace, extract_cluster_rewards
except ImportError:
    def load_json_trace(path):
        """Fallback function when metrics logger is not available"""
        return {}
    def extract_cluster_rewards(trace):
        """Fallback function when metrics logger is not available"""
        return {}

def plot_cluster_reward(trace_json_path, output="results/processed/cluster_rewards.png", window=5):
    # Load and extract
    trace = load_json_trace(trace_json_path)
    cluster_rewards = extract_cluster_rewards(trace)

    # Style
    plt.figure(figsize=(8, 5))
    plt.rcParams.update({'font.size': 12})
    color_map = plt.get_cmap("tab10")

    # Plot each cluster’s smoothed reward
    
    for i, (cid, rewards) in enumerate(sorted(cluster_rewards.items())):
        rewards = np.array(rewards)
        if len(rewards) >= window:
            smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
            plt.plot(smoothed, label=f"Cluster {cid}", color=color_map(i), linewidth=2)
        else:
            plt.plot(rewards, label=f"Cluster {cid}", color=color_map(i), linewidth=2)

    # Axis & labels
    plt.xlabel("Step", fontsize=13)
    plt.ylabel("Smoothed Reward", fontsize=13)
    plt.title("Per-Cluster Reward Trends", fontsize=14, weight='bold')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(output, dpi=500)
    print(f"✅ Saved → {output}")
    plt.show()
    plt.close()


if __name__ == "__main__":
    plot_cluster_reward("results/fedsemgnn_trace.json")
