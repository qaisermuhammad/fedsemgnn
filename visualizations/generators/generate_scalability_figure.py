#!/usr/bin/env python3
"""Generate publication-quality scalability analysis figure for the paper.

Reads results/scalability/scalability_results.csv and produces:
  figures/scalability_analysis.png  — 2x2 subplot (latency, power, time/step, reward)
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "results", "scalability", "scalability_results.csv")
OUT_PATH = os.path.join(PROJECT_ROOT, "figures", "scalability_analysis.png")

def main():
    df = pd.read_csv(CSV_PATH)
    df = df.sort_values("node_count").reset_index(drop=True)
    
    nodes = df["node_count"].values
    latency = df["avg_latency_ms"].values
    power = df["avg_power_w"].values
    time_step = df["time_per_step_s"].values
    reward = df["avg_reward"].values
    
    print("Scalability data:")
    for i, n in enumerate(nodes):
        print(f"  {n:>5d} nodes: lat={latency[i]:.2f}ms, pwr={power[i]:.1f}W, "
              f"t/step={time_step[i]:.3f}s, reward={reward[i]:.4f}")
    
    # --- Publication Figure ---
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("FedSemGNN Scalability Analysis (6 – {:,} Nodes)".format(int(nodes[-1])),
                 fontsize=14, fontweight="bold", y=0.98)
    
    marker_style = dict(marker='o', markersize=7, linewidth=2.0, color='#2166ac')
    
    # (a) Orchestration Latency
    ax = axes[0, 0]
    ax.plot(nodes, latency, **marker_style)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Number of Edge Nodes", fontsize=11)
    ax.set_ylabel("Avg Latency (ms)", fontsize=11)
    ax.set_title("(a) Orchestration Latency", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    # Annotate key points
    for i in [0, len(nodes)//2, -1]:
        ax.annotate(f"{latency[i]:.1f}ms",
                    (nodes[i], latency[i]),
                    textcoords="offset points", xytext=(5, 10),
                    fontsize=8, ha='left')
    
    # (b) Power Consumption
    ax = axes[0, 1]
    ax.plot(nodes, power, **marker_style)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Number of Edge Nodes", fontsize=11)
    ax.set_ylabel("Avg Power (W)", fontsize=11)
    ax.set_title("(b) Power Consumption", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    # Fit linear scaling line
    slope_power = np.polyfit(np.log10(nodes), np.log10(power), 1)
    ax.annotate(f"Slope: {slope_power[0]:.2f}",
                xy=(0.05, 0.92), xycoords='axes fraction',
                fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))
    
    # (c) Computation Time per Step
    ax = axes[1, 0]
    ax.plot(nodes, time_step, **marker_style)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Number of Edge Nodes", fontsize=11)
    ax.set_ylabel("Time per Step (s)", fontsize=11)
    ax.set_title("(c) Computation Time per Step", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    slope_time = np.polyfit(np.log10(nodes), np.log10(time_step), 1)
    ax.annotate(f"Slope: {slope_time[0]:.2f}",
                xy=(0.05, 0.92), xycoords='axes fraction',
                fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))
    
    # (d) Reward
    ax = axes[1, 1]
    ax.plot(nodes, reward, **marker_style)
    ax.set_xscale('log')
    ax.set_xlabel("Number of Edge Nodes", fontsize=11)
    ax.set_ylabel("Avg Normalized Reward", fontsize=11)
    ax.set_title("(d) Reward Convergence", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    plt.savefig(OUT_PATH, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to {OUT_PATH}")
    
    # Print summary statistics for paper
    print("\n=== PAPER STATISTICS ===")
    ratio_lat = latency[-1] / latency[0]
    ratio_power = power[-1] / power[0]
    ratio_nodes = nodes[-1] / nodes[0]
    print(f"Scale range: {nodes[0]} -> {nodes[-1]} ({ratio_nodes:.0f}x)")
    print(f"Latency scaling: {latency[0]:.2f}ms -> {latency[-1]:.2f}ms ({ratio_lat:.1f}x increase over {ratio_nodes:.0f}x nodes)")
    print(f"Power scaling: {power[0]:.1f}W -> {power[-1]:.1f}W ({ratio_power:.1f}x increase over {ratio_nodes:.0f}x nodes)")
    print(f"Power per node: {power[0]/nodes[0]:.2f}W/node (small) vs {power[-1]/nodes[-1]:.2f}W/node (large)")
    print(f"Time/step scaling: {time_step[0]:.3f}s -> {time_step[-1]:.3f}s")
    print(f"Log-log slope (power): {slope_power[0]:.3f}")
    print(f"Log-log slope (time/step): {slope_time[0]:.3f}")
    

if __name__ == "__main__":
    main()
