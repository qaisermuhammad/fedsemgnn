# power_consumption.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

STRATEGY_SOURCES = {
    "FedSemGNN": r"results/fedsemgnn_metrics.csv",
    "HSQF Heur.": r"results/hsqf_metrics.csv",
    "Random": r"results/random_place_metrics.csv",
    "HierFedPPO": r"results/hier_fedppo_metrics.csv",
    "FlatFedPPO": r"results/flat_fedppo_metrics.csv"
}

OUT_PNG = "graphs/power_consumption.png"
OUT_PDF = "graphs/power_consumption.pdf"

def mean_power(csv_path: str) -> float:
    df = pd.read_csv(csv_path)
    col = "Power_W"
    if col not in df.columns:
        raise ValueError(f"{csv_path} missing '{col}' column")
    return float(df[col].dropna().astype(float).mean())

def main():
    names, vals = [], []
    for name, path in STRATEGY_SOURCES.items():
        if Path(path).exists():
            names.append(name)
            vals.append(mean_power(path))
        else:
            print(f"⚠️ Missing file for '{name}': {path}")
    if not vals:
        raise SystemExit("No CSVs found.")

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(names, vals)
    ax.set_title("Power Consumption ▲ Lower is Better", fontsize=16)
    ax.set_ylabel("Power (Watts)")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + max(vals)*0.02,
                f"{v:.1f}W", ha="center", va="bottom", fontsize=11)
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=500)
    plt.savefig(OUT_PDF)
    print(f"✅ Saved {OUT_PNG}, {OUT_PDF}")

if __name__ == "__main__":
    main()
