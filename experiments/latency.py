# latency.py (fixed)
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

STRATEGY_SOURCES = {
    "FedSemGNN":    r"results/fedsemgnn_metrics.csv",
    "HSQF Heur.":   r"results/hsqf_metrics.csv",
    "Random":       r"results/random_place_metrics.csv",
    "HierFedPPO":   r"results/hier_fedppo_metrics.csv",
    "FlatFedPPO":   r"results/flat_fedppo_metrics.csv",
}

OUT_PNG = "graphs/latency.png"
OUT_PDF = "graphs/latency.pdf"

LAST_K = 100           # match the paper’s “last 100 steps”
PLOT_UNITS = "seconds" # choose "seconds" or "ms"

def mean_latency(csv_path: str) -> float:
    df = pd.read_csv(csv_path)
    if "Latency_ms" not in df.columns:
        raise ValueError(f"{csv_path} missing 'Latency_ms' column")
    s = df["Latency_ms"].dropna().astype(float)
    if LAST_K is not None and len(s) > LAST_K:
        s = s.tail(LAST_K)
    # Canonical assumption: the column is in milliseconds.
    mean_ms = float(s.mean())
    if PLOT_UNITS == "seconds":
        return mean_ms / 1000.0
    elif PLOT_UNITS == "ms":
        return mean_ms
    else:
        raise ValueError("PLOT_UNITS must be 'seconds' or 'ms'.")

def main():
    names, vals = [], []
    for name, path in STRATEGY_SOURCES.items():
        if Path(path).exists():
            names.append(name)
            vals.append(mean_latency(path))
        else:
            print(f"⚠️ Missing file for '{name}': {path}")
    if not vals:
        raise SystemExit("No CSVs found.")

    ylabel = "Latency (seconds)" if PLOT_UNITS == "seconds" else "Latency (ms)"
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(names, vals)
    ax.set_title(f"Latency Comparison (mean of last {LAST_K} steps) ▲ Lower is Better", fontsize=16)
    ax.set_ylabel(ylabel)
    ymax = max(vals) if vals else 1.0
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + ymax*0.02,
                f"{v:.2f}{'s' if PLOT_UNITS=='seconds' else ' ms'}",
                ha="center", va="bottom", fontsize=11)
    plt.tight_layout()
    Path("graphs").mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PNG, dpi=500)
    plt.savefig(OUT_PDF)
    print(f"✅ Saved {OUT_PNG}, {OUT_PDF}")

if __name__ == "__main__":
    main()
