# plot_diagnostics.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Handle metrics logger import with fallback
try:
    from ..metrics.metrics_logger import aggregate_runs
except ImportError:
    try:
        from analysis.metrics.metrics_logger import aggregate_runs
    except ImportError:
        # Fallback function if metrics logger is not available
        def aggregate_runs(*args, **kwargs):
            """Fallback function when metrics logger is not available"""
            return [], []

import os

def plot_reward_with_confidence(run_dir, out_file="reward_with_ci.png"):
    mean_r, std_r = aggregate_runs(run_dir)
    steps = np.arange(len(mean_r))

    plt.figure()
    plt.plot(steps, mean_r, label='Mean Reward')
    plt.fill_between(steps, mean_r - std_r, mean_r + std_r, alpha=0.3, label='±1 Std Dev')
    plt.xlabel("Steps")
    plt.ylabel("Reward")
    plt.title("Reward over Time with Confidence Interval")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_file, dpi=500)
    plt.show()
    plt.close()
    print(f"✅ Saved → {out_file}")

def plot_train_vs_val(train_file, val_file, out_file="train_val_reward.png"):
    train = np.loadtxt(train_file, delimiter=',', skiprows=1, usecols=[2])  # Adjust column index if needed
    val = np.loadtxt(val_file, delimiter=',', skiprows=1, usecols=[2])
    steps = np.arange(len(train))

    plt.figure()
    plt.plot(steps, train, label='Training Reward')
    plt.plot(steps, val, label='Validation Reward')
    plt.xlabel("Steps")
    plt.ylabel("Reward")
    plt.title("Train vs. Validation Reward")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_file, dpi=500)
    plt.show()
    plt.close()
    print(f"✅ Saved → {out_file}")


if __name__ == "__main__":
    # ✅ CHANGE THIS PATH to your actual directory containing run_*.csv files
    run_dir = "results/run_default/runs"  # or whatever your logging dir is

    if os.path.exists(run_dir):
        plot_reward_with_confidence(run_dir)
    else:
        print(f"❌ Directory not found: {run_dir}")
    
    # Optional: Uncomment below if you have split files
    # plot_train_vs_val("results/train_reward.csv", "results/val_reward.csv")
