#!/usr/bin/env python3
"""
Generate proper multi-trial statistical significance figure.
Uses actual 5-trial data from results/multi_trial/ to create:
  - Box/strip plots showing trial-level variation per algorithm
  - p-value annotations from between-trial Mann-Whitney U tests
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import csv
import os
import sys
from scipy.stats import mannwhitneyu

csv.field_size_limit(10**7)

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MULTI_TRIAL_DIR = os.path.join(PROJECT, "results", "multi_trial")

ALGOS = [
    ("FedSemGNN", "fedsemgnn"),
    ("FlatFedPPO", "flatfedppo"),
    ("HierFedPPO", "hierfedppo"),
    ("HSQF", "hsqf"),
    ("RandomPlacement", "randomplacement"),
    ("CentralizedPPO", "centralizedppo"),
]

COLORS = {
    "FedSemGNN": "#1f77b4",
    "FlatFedPPO": "#ff7f0e",
    "HierFedPPO": "#2ca02c",
    "HSQF": "#d62728",
    "RandomPlacement": "#9467bd",
    "CentralizedPPO": "#8c564b",
}


def load_trial_means(algo_dir, n_trials=5):
    """Load per-trial mean latency and fidelity from archived CSVs."""
    latencies = []
    fidelities = []
    rewards = []
    powers = []
    for t in range(1, n_trials + 1):
        path = os.path.join(algo_dir, f"trial_{t}.csv")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            rows = list(csv.DictReader(f))
        lats = [float(r["Latency_ms"]) for r in rows]
        fids = [float(r["Fidelity_pct"]) for r in rows]
        rews = [float(r["Reward"]) for r in rows]
        pows = [float(r["Power_W"]) for r in rows]
        latencies.append(np.mean(lats))
        fidelities.append(np.mean(fids))
        rewards.append(np.mean(rews))
        powers.append(np.mean(pows))
    return {
        "latency": np.array(latencies),
        "fidelity": np.array(fidelities),
        "reward": np.array(rewards),
        "power": np.array(powers),
    }


def main():
    # Load all trial data
    all_data = {}
    for display_name, folder_name in ALGOS:
        algo_dir = os.path.join(MULTI_TRIAL_DIR, folder_name)
        data = load_trial_means(algo_dir)
        all_data[display_name] = data
        print(f"{display_name}: {len(data['latency'])} trials loaded")
        print(f"  Latency: {np.mean(data['latency']):.2f} ± {np.std(data['latency']):.2f}")
        print(f"  Fidelity: {np.mean(data['fidelity']):.2f} ± {np.std(data['fidelity']):.2f}")

    algo_names = [name for name, _ in ALGOS]
    n_algos = len(algo_names)

    # Create figure: 2x2 subplots — latency, fidelity, reward, power
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    metrics = [
        ("latency", "Orchestration Latency (ms)", axes[0, 0]),
        ("fidelity", "Semantic Fidelity (%)", axes[0, 1]),
        ("reward", "Reward", axes[1, 0]),
        ("power", "Power (W)", axes[1, 1]),
    ]

    for metric_key, ylabel, ax in metrics:
        positions = range(n_algos)
        box_data = [all_data[name][metric_key] for name in algo_names]

        # Box plots
        bp = ax.boxplot(
            box_data,
            positions=positions,
            widths=0.5,
            patch_artist=True,
            showfliers=True,
            showmeans=True,
            meanprops=dict(marker="D", markerfacecolor="black", markersize=6),
        )
        for patch, name in zip(bp["boxes"], algo_names):
            patch.set_facecolor(COLORS[name])
            patch.set_alpha(0.7)

        # Overlay individual trial points
        for i, name in enumerate(algo_names):
            y = all_data[name][metric_key]
            x = np.full_like(y, i) + np.random.normal(0, 0.05, len(y))
            ax.scatter(x, y, color=COLORS[name], s=30, zorder=5, edgecolors="black", linewidth=0.5)

        ax.set_xticks(positions)
        ax.set_xticklabels(algo_names, rotation=25, ha="right", fontsize=9)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.grid(True, alpha=0.3, axis="y")

        # Mann-Whitney U: FedSemGNN vs each baseline
        fed_data = all_data["FedSemGNN"][metric_key]
        for i, name in enumerate(algo_names[1:], 1):
            base_data = all_data[name][metric_key]
            if len(fed_data) >= 3 and len(base_data) >= 3:
                try:
                    stat, p = mannwhitneyu(fed_data, base_data, alternative="two-sided")
                    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                except:
                    sig = "n/a"
            else:
                sig = "n/a"
            # Don't annotate if too crowded — just add to title or text
            ymax = max(max(fed_data), max(base_data))
            # Small annotation above the baseline box
            ax.annotate(
                sig,
                xy=(i, ymax),
                xytext=(i, ymax + 0.03 * (ax.get_ylim()[1] - ax.get_ylim()[0])),
                ha="center",
                fontsize=8,
                color="red" if sig != "ns" else "gray",
            )

    fig.suptitle(
        "Multi-Trial Statistical Validation (5 Independent Trials per Algorithm)\n"
        "Box plots with individual trial points; significance vs FedSemGNN: *p<0.05, **p<0.01, ***p<0.001",
        fontsize=12,
        fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])

    for outdir in ["graphs", "figures"]:
        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, "statistical_significance_analysis.png")
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        print(f"Saved {outpath}")
    plt.close()

    # Also print p-value matrix for documentation
    print("\n\nP-VALUE MATRIX (Mann-Whitney U, reward metric):")
    print(f"{'':>18}", end="")
    for name in algo_names:
        print(f"  {name:>16}", end="")
    print()
    for i, name_i in enumerate(algo_names):
        print(f"{name_i:>18}", end="")
        for j, name_j in enumerate(algo_names):
            if i == j:
                print(f"{'---':>18}", end="")
            else:
                try:
                    _, p = mannwhitneyu(
                        all_data[name_i]["latency"],
                        all_data[name_j]["latency"],
                        alternative="two-sided",
                    )
                    print(f"{p:>18.4f}", end="")
                except:
                    print(f"{'n/a':>18}", end="")
        print()

    print("\nDone!")


if __name__ == "__main__":
    main()
