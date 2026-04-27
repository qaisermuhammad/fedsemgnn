# fidelity.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

STRATEGY_SOURCES = {
    "FedSemGNN": r"results/fedsemgnn_metrics.csv",
    "FlatFedPPO": r"results/flat_fedppo_metrics.csv",
    "HierFedPPO": r"results/hier_fedppo_metrics.csv",
    "HSQF":       r"results/hsqf_metrics.csv",
    "Random":     r"results/random_place_metrics.csv",
}


OUT_PNG = "graphs/fidelity.png"
OUT_PDF = "graphs/fidelity.pdf"

def mean_fidelity(csv_path: str) -> float:
    df = pd.read_csv(csv_path)
    col = "Fidelity_pct"
    if col not in df.columns:
        raise ValueError(f"{csv_path} missing '{col}' column")
    s = df[col].dropna().astype(float)
    # If values look like 0..1, convert to %
    val = 100.0 * s.mean() if s.mean() <= 1.0 else s.mean()
    return float(val)

def main():
    names, vals = [], []
    for name, path in STRATEGY_SOURCES.items():
        if Path(path).exists():
            names.append(name)
            vals.append(mean_fidelity(path))
        else:
            print(f"⚠️ Missing file for '{name}': {path}")
    if not vals:
        raise SystemExit("No CSVs found.")

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(names, vals)
    ax.set_title("Semantic Fidelity ▲ Higher is Better", fontsize=16)
    ax.set_ylabel("Fidelity (%)")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + max(vals)*0.02,
                f"{v:.1f}%", ha="center", va="bottom", fontsize=11)
    plt.ylim(0, max(100, max(vals)*1.15))
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=500)
    plt.savefig(OUT_PDF)
    print(f"✅ Saved {OUT_PNG}, {OUT_PDF}")

if __name__ == "__main__":
    main()
