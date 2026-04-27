#plot_normalized_metrics.py
#Run directly in your IDE. No command-line args required.

import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List

# ========= CONFIG (edit in IDE) =========
INPUTS = [
    ("FedSemGNN", r"results/fedsemgnn_metrics.csv"),
    ("HSQF Heur.", r"results/hsqf_metrics.csv"),
    ("Random", r"results/random_place_metrics.csv"),
    ("HierFedPPO", r"results/hier_fedppo_metrics.csv"),
    ("FlatFedPPO", r"results/flat_fedppo_metrics.csv")
]


OUTDIR = r"logs/normalized_plots"
SMOOTH = 5            # rolling window (steps). Set to 1 to disable smoothing.
NORMALIZE_MODE = "minmax"  # "minmax" | "zscore" | "relative" (needs a baseline)
BASELINE_LABEL = "Random"  # only used if NORMALIZE_MODE == "relative"
# ========================================

# Column name fallbacks per metric
CANDIDATES = {
    "step": ["step", "t", "epoch", "iteration"],
    "reward": ["reward", "reward_step", "reward_per_step", "reward_scaled"],
    "latency": ["latency", "latency_ms", "orchestration_latency_ms", "decision_latency_ms"],
    "fidelity": ["fidelity", "fidelity_pct", "semantic_fidelity", "fidelity_percent"],
}

def _find_col(df: pd.DataFrame, keys: List[str]) -> Optional[str]:
    cols_lower = {c.lower(): c for c in df.columns}
    for k in keys:
        if k in cols_lower:
            return cols_lower[k]
    return None

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _smooth(s: pd.Series, window: int) -> pd.Series:
    if window is None or window <= 1:
        return s
    return s.rolling(window=window, min_periods=1, center=False).mean()

def _normalize(series: pd.Series, mode: str, baseline: Optional[pd.Series] = None) -> pd.Series:
    s = series.astype(float)
    if mode == "minmax":
        s_min, s_max = float(np.nanmin(s)), float(np.nanmax(s))
        if math.isclose(s_max, s_min):
            return pd.Series(np.zeros_like(s), index=s.index)
        return (s - s_min) / (s_max - s_min)
    elif mode == "zscore":
        mu, sigma = float(np.nanmean(s)), float(np.nanstd(s))
        if math.isclose(sigma, 0.0):
            return pd.Series(np.zeros_like(s), index=s.index)
        return (s - mu) / sigma
    elif mode == "relative":
        if baseline is None:
            raise ValueError("relative mode requires a baseline series")
        b = baseline.astype(float)
        # Avoid division by zero: add tiny epsilon
        eps = 1e-9
        return (s - b) / (np.abs(b) + eps)
    else:
        raise ValueError(f"Unknown normalize mode: {mode}")

def _load_metric(df: pd.DataFrame, metric: str) -> pd.Series:
    col = _find_col(df, CANDIDATES[metric])
    if col is None:
        raise ValueError(f"Could not find a column for '{metric}' in CSV. "
                         f"Looked for: {CANDIDATES[metric]}. Found: {list(df.columns)}")
    s = df[col]
    # Fidelity heuristics: if values look like 0..1, convert to %
    if metric == "fidelity":
        s = pd.to_numeric(s, errors="coerce")
        if s.dropna().between(0, 1).mean() > 0.9:
            s = s * 100.0
    return s

def _load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # try to sort by step if present
    step_col = _find_col(df, CANDIDATES["step"])
    if step_col:
        df = df.sort_values(by=step_col).reset_index(drop=True)
    return df

def _plot_metric(
    inputs: List[Tuple[str, str]],
    metric: str,
    outdir: str,
    mode: str,
    smooth: int,
    baseline_label: Optional[str] = None,
    title: Optional[str] = None,
):
    _ensure_dir(outdir)

    # Load all
    loaded = []
    for label, path in inputs:
        df = _load_csv(path)
        step_col = _find_col(df, CANDIDATES["step"])
        x = df[step_col] if step_col else pd.Series(range(len(df)))
        y = _load_metric(df, metric)
        y = _smooth(y, smooth)
        loaded.append((label, x, y))

    # Prepare baseline if relative
    baseline_series = None
    if mode == "relative":
        if baseline_label is None:
            raise ValueError("relative mode requires BASELINE_LABEL")
        candidates = [y for (lbl, _, y) in loaded if lbl == baseline_label]
        if not candidates:
            raise ValueError(f"Baseline label '{baseline_label}' not found in INPUTS")
        baseline_series = candidates[0]

    # Plot
    plt.figure(figsize=(7, 4))
    for label, x, y in loaded:
        norm_y = _normalize(y, mode, baseline=baseline_series)
        plt.plot(x, norm_y, label=label, linewidth=1.8)

    plt.xlabel("Step")
    y_label = {
        "reward": "Normalized Reward",
        "latency": "Normalized Latency",
        "fidelity": "Normalized Fidelity"
    }[metric]
    plt.ylabel(y_label + (f" ({mode})" if mode != "minmax" else ""))
    plt.title(title or f"Normalized {metric.capitalize()} ({mode})")
    plt.grid(True, alpha=0.25)
    if len(loaded) > 1:
        plt.legend()
    fname = os.path.join(outdir, f"normalized_{metric}_{mode}.png")
    plt.tight_layout()
    plt.savefig(fname, dpi=500)
    plt.close()
    print(f"✅ saved: {fname}")

def main():
    # Single-strategy run (FedSemGNN only).
    # If you later add baselines, just append to INPUTS above and optionally switch NORMALIZE_MODE to "relative".
    for metric in ["reward", "latency", "fidelity"]:
        _plot_metric(
            INPUTS,
            metric=metric,
            outdir=OUTDIR,
            mode=NORMALIZE_MODE,
            smooth=SMOOTH,
            baseline_label=BASELINE_LABEL,
            title=f"FedSemGNN Normalized {metric.capitalize()}",
        )

if __name__ == "__main__":
    main()
