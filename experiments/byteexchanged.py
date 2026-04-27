# byteexchanged.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---- Map each strategy name to its metrics CSV ----
STRATEGY_SOURCES = {
    "FedSemGNN": r"results/fedsemgnn_metrics.csv",
    "HSQF Heur.": r"results/hsqf_metrics.csv",
    "Random": r"results/random_place_metrics.csv",
    "HierFedPPO": r"results/hier_fedppo_metrics.csv",
    "FlatFedPPO": r"results/flat_fedppo_metrics.csv"
}

OUT_PNG = r"graphs/bytes_newfolder/bytes_exchanged.png"
OUT_PDF = r"graphs/bytes_newfolder/bytes_exchanged.pdf"

def load_total_mb(csv_path: str) -> float:
    df = pd.read_csv(csv_path)
    col = "Bytes_step_MB"
    if col not in df.columns:
        raise ValueError(f"{csv_path} missing '{col}' column")
    # Auto-scale to MB if values look like bytes; if already MB, this keeps numbers sane
    s = df[col].astype(float)
    mean_val = s[s.notna()].mean()
    # Heuristic: if mean is large (>1e4) assume bytes; else assume MB already
    total_mb = s.sum() / 1e6 if mean_val > 1e4 else s.sum()
    return float(total_mb)

def main():
    names, totals = [], []
    for name, path in STRATEGY_SOURCES.items():
        if Path(path).exists():
            names.append(name)
            totals.append(load_total_mb(path))
        else:
            print(f"⚠️ Missing file for '{name}': {path}")

    if not totals:
        raise SystemExit("No CSVs found. Update STRATEGY_SOURCES paths.")

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(names, totals)
    ax.set_title("Communication Overhead ▼ Lower is Better", fontsize=16)
    ax.set_ylabel("Bytes Exchanged (MB)")
    for b, v in zip(bars, totals):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + max(totals)*0.02,
                f"{v:.1f}MB", ha="center", va="bottom", fontsize=11)
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=500)
    plt.savefig(OUT_PDF)
    print(f"✅ Saved {OUT_PNG}, {OUT_PDF}")

if __name__ == "__main__":
    main()
