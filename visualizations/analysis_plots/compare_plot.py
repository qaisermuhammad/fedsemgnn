# make_compare_plots.py
# Create one consolidated plot per metric (all 5 strategies).
# Expected CSV schema (case-insensitive, flexible): 
#   Step, Reward, Latency_ms, Fidelity_pct, Bytes_step_MB, Bytes_cum_MB, Power_W, Migrations
# Any missing metric -> that plot is skipped for that strategy (you'll see a notice).

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

# ----------------------------
# Config
# ----------------------------
# Update these paths if your files live elsewhere.
csv_paths: Dict[str, str] = {
    "FedSemGNN":      "results/fedsemgnn_metrics.csv",
    "FlatFedPPO":     "results/flat_fedppo_metrics.csv",
    "HierFedPPO":     "results/hier_fedppo_metrics.csv",
    "HSQF":           "results/hsqf_metrics.csv",
    "Random":         "results/random_place_metrics.csv",
}

out_dir = "results/plots_compare"
os.makedirs(out_dir, exist_ok=True)

# Gentle smoothing for readability (set to 1 for no smoothing)
SMOOTH_WINDOW = 5

# IEEE-friendly, colorblind-safe palette (high contrast)
# (Tab10 subset): black, blue, orange, green, red
colors = {
    "FedSemGNN":  "#000000",  # black
    "FlatFedPPO": "#1f77b4",  # blue
    "HierFedPPO": "#ff7f0e",  # orange
    "HSQF":       "#2ca02c",  # green
    "Random":     "#d62728",  # red
}

linestyles = {
    "FedSemGNN":  "-",
    "FlatFedPPO": "--",
    "HierFedPPO": "-.",
    "HSQF":       ":",
    "Random":     (0, (3, 1, 1, 1)),  # dash-dot-dot
}

# Matplotlib styling tuned for print
plt.rcParams.update({
    "font.family": "serif",          # Times/serif is typical for IEEE figures
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "lines.linewidth": 2.0,
    "savefig.dpi": 500,
    "figure.dpi": 500,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ----------------------------
# Helpers
# ----------------------------
ALIASES = {
    "step": ["step", "Step", "t", "epoch"],
    "reward": ["reward", "Reward"],
    "latency_ms": ["latency_ms", "Latency_ms", "latency", "Latency"],
    "fidelity_pct": ["fidelity_pct", "Fidelity_pct", "fidelity", "Fidelity"],
    "bytes_step_mb": ["bytes_step_mb", "Bytes_step_MB", "bytes_step", "Bytes_step"],
    "bytes_cum_mb": ["bytes_cum_mb", "Bytes_cum_MB", "bytes_cum", "Bytes_cum"],
    "power_w": ["power_w", "Power_W", "power", "Power"],
    "migrations": ["migrations", "Migrations"],
}

def find_col(df: pd.DataFrame, keys: List[str]) -> str:
    cols_lower = {c.lower(): c for c in df.columns}
    for k in keys:
        if k.lower() in cols_lower:
            return cols_lower[k.lower()]
    return ""

def load_unified(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"[skip] {path}: file not found")
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Map required columns if present
    out = {}
    for logical, candidates in ALIASES.items():
        col = find_col(df, candidates)
        if col:
            out[logical] = df[col].values
    # Must have Step to be plottable
    if "step" not in out:
        print(f"[skip] {path}: missing required column 'Step'")
        return pd.DataFrame()
    return pd.DataFrame(out)

def smooth_series(s: pd.Series, window: int) -> pd.Series:
    if window <= 1:
        return s
    return s.rolling(window, min_periods=1, center=False).mean()

def plot_lines(metric_key: str,
               y_label: str,
               out_name: str,
               logy: bool = False,
               ylim: tuple = None,
               smooth_window: int = SMOOTH_WINDOW):
    plt.figure(figsize=(6.0, 3.2))  # Good for single-column width in IEEE
    plotted_any = False
    for strategy, path in csv_paths.items():
        df = load_unified(path)
        if df.empty:
            continue
        if metric_key not in df.columns:
            print(f"[skip] {strategy}: missing column for {y_label} -> {metric_key}")
            continue
        x = df["step"]
        y = pd.Series(df[metric_key], index=x.index)
        y_s = smooth_series(y, smooth_window)
        plt.plot(x, y_s, label=strategy,
                 color=colors.get(strategy, None),
                 linestyle=linestyles.get(strategy, "-"))
        plotted_any = True

    if not plotted_any:
        print(f"[info] No data available to plot: {y_label}")
        plt.close()
        return

    plt.xlabel("Step")
    plt.ylabel(y_label)
    if logy:
        plt.yscale("log")
    if ylim is not None:
        plt.ylim(*ylim)
    plt.grid(True, alpha=0.25, linewidth=0.8)
    # Put legend outside to avoid overlap, but keep compact
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, frameon=True)
    plt.tight_layout()
    out_path = os.path.join(out_dir, out_name)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[ok] saved: {out_path}")

# ----------------------------
# Generate plots
# ----------------------------
# 1) Reward (linear)
plot_lines(metric_key="reward",
           y_label="Reward (per step)",
           out_name="compare_reward.png",
           logy=False)

# 2) Latency (linear)
plot_lines(metric_key="latency_ms",
           y_label="Orchestration Latency (ms)",
           out_name="compare_latency_linear.png",
           logy=False)

# 3) Latency (log scale) — very helpful when ranges differ by orders of magnitude
plot_lines(metric_key="latency_ms",
           y_label="Orchestration Latency (ms, log)",
           out_name="compare_latency_log.png",
           logy=True)

# 4) Fidelity (percentage, linear)
plot_lines(metric_key="fidelity_pct",
           y_label="Fidelity (%)",
           out_name="compare_fidelity.png",
           logy=False,
           ylim=(0, 100))

# 5) Power (Watts, linear)
plot_lines(metric_key="power_w",
           y_label="Power (W)",
           out_name="compare_power.png",
           logy=False)

# 6) Communication — per-step bytes (MB)
plot_lines(metric_key="bytes_step_mb",
           y_label="Bytes per Step (MB)",
           out_name="compare_bytes_step.png",
           logy=False)

# 7) Communication — cumulative bytes (MB)
plot_lines(metric_key="bytes_cum_mb",
           y_label="Cumulative Bytes (MB)",
           out_name="compare_bytes_cumulative.png",
           logy=False)

# ----------------------------
# (Optional) Normalized plots (min–max per strategy), helpful to compare trends
# ----------------------------
def plot_normalized(metric_key: str, y_label: str, out_name: str):
    plt.figure(figsize=(6.0, 3.2))
    plotted_any = False
    for strategy, path in csv_paths.items():
        df = load_unified(path)
        if df.empty or metric_key not in df.columns:
            continue
        x = df["step"]
        y = pd.Series(df[metric_key], index=x.index).astype(float)
        # Min–max per strategy
        y_min, y_max = y.min(), y.max()
        if np.isfinite(y_min) and np.isfinite(y_max) and y_max > y_min:
            y_norm = (y - y_min) / (y_max - y_min)
        else:
            y_norm = y * 0.0  # flat if no variation
        y_norm = smooth_series(y_norm, SMOOTH_WINDOW)
        plt.plot(x, y_norm, label=strategy,
                 color=colors.get(strategy, None),
                 linestyle=linestyles.get(strategy, "-"))
        plotted_any = True

    if not plotted_any:
        print(f"[info] No data available to plot: {y_label} (normalized)")
        plt.close()
        return

    plt.xlabel("Step")
    plt.ylabel(y_label + " (Normalized)")
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.25, linewidth=0.8)
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, frameon=True)
    plt.tight_layout()
    out_path = os.path.join(out_dir, out_name)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[ok] saved: {out_path}")

# Normalized versions (optional but useful)
plot_normalized("reward",      "Reward",        "normalized_reward_minmax_all.png")
plot_normalized("latency_ms",  "Latency (ms)",  "normalized_latency_minmax_all.png")
plot_normalized("fidelity_pct","Fidelity (%)",  "normalized_fidelity_minmax_all.png")
