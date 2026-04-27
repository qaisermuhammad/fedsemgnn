# plot_recovery_and_bytes.py
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DEF_CSV = Path("results/fedsemgnn_metrics.csv")
DEF_OUTDIR = Path("graphs/bytes")
DEF_WINDOW = 5  # moving avg window for smoothing the bytes-per-step curve

REQUIRED_MAP = {
    "step": ["Step"],
    "migrations": ["Migrations", "migrations"],
    "fidelity": ["Fidelity_pct"],
    "bytes": ["Bytes_step_MB"],
}

def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def estimate_recovery_lag(fidelity_series, thresh_drop=0.05, recover_eps=0.01, max_lookahead=200):
    """
    Very simple heuristic:
      - When fidelity drops by >= thresh_drop from the previous step, mark a 'dip start'.
      - Recovery lag = number of steps until fidelity returns to within 'recover_eps' of the pre-dip level.
      - If not recovered within max_lookahead, cap at that.
    Returns a series 'lag' aligned to input index with NaNs where no dip is evaluated that step.
    """
    f = fidelity_series.values.astype(float)
    lag = np.full_like(f, np.nan, dtype=float)

    for i in range(1, len(f)):
        prev = f[i-1]
        cur = f[i]
        if prev - cur >= thresh_drop:
            # dip detected at i
            target = prev - recover_eps  # consider recovered once back near pre-dip
            steps = 0
            j = i
            recovered = False
            while j < len(f) and steps < max_lookahead:
                if f[j] >= target:
                    recovered = True
                    break
                steps += 1
                j += 1
            lag[i] = steps if recovered else np.nan
    return pd.Series(lag, index=fidelity_series.index)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default=str(DEF_CSV),
                    help=f"Path to metrics CSV (default: {DEF_CSV})")
    ap.add_argument("--outdir", type=str, default=str(DEF_OUTDIR),
                    help=f"Directory to save figures/logs (default: {DEF_OUTDIR})")
    ap.add_argument("--window", type=int, default=DEF_WINDOW,
                    help="Moving average window for smoothing per-step bytes (default: 5)")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Map your actual column names to normalized names
    col_map = {}
    for norm, cands in REQUIRED_MAP.items():
        found = find_col(df, cands)
        if not found:
            raise ValueError(f"CSV must contain one of columns for '{norm}': {cands}\n"
                             f"Found columns: {list(df.columns)}")
        col_map[norm] = found

    # Build a working frame with normalized columns
    w = pd.DataFrame({
        "step": df[col_map["step"]],
        "migrations": df[col_map["migrations"]],
        "fidelity": df[col_map["fidelity"]],
        "bytes_raw": df[col_map["bytes"]],
    }).copy()

    # If BytesExchanged looks like bytes, convert to MB.
    # Heuristic: if median > 1e3 it's likely bytes; if already small (<10), might be MB already.
    med = pd.to_numeric(w["bytes_raw"], errors="coerce").median()
    if pd.isna(med):
        med = 0.0
    if med > 1024:  # assume bytes → MB
        w["bytes_mb_step"] = w["bytes_raw"] / (1024 * 1024)
    else:
        # assume already MB (or very small byte counts); keep as-is
        w["bytes_mb_step"] = w["bytes_raw"].astype(float)

    # Cumulative MB over time
    w["bytes_mb_cum"] = w["bytes_mb_step"].cumsum()

    # Smooth per-step bytes for a cleaner plot
    if args.window > 1:
        w["bytes_mb_step_smooth"] = w["bytes_mb_step"].rolling(args.window, min_periods=1).mean()
    else:
        w["bytes_mb_step_smooth"] = w["bytes_mb_step"]

    # Fidelity recovery lag (heuristic)
    w["recovery_lag"] = estimate_recovery_lag(w["fidelity"].astype(float))

    # Save processed logs
    processed_csv = outdir / "processed_bytes_and_recovery.csv"
    w.to_csv(processed_csv, index=False)

    # --- Plot 1: Bytes exchanged (per-step and cumulative) ---
    plt.figure(figsize=(8, 4))
    plt.plot(w["step"], w["bytes_mb_step_smooth"], label="Per-step (MB)")
    plt.plot(w["step"], w["bytes_mb_cum"], label="Cumulative (MB)", linestyle="--")
    plt.xlabel("Step")
    plt.ylabel("MB")
    plt.title("Bytes Exchanged Over Time")
    plt.legend()
    plt.tight_layout()
    bytes_fig = outdir / "bytes_exchanged.png"
    plt.savefig(bytes_fig, dpi=500)
    plt.close()

    # --- Plot 2: Recovery lag (estimated from fidelity dips) ---
    plt.figure(figsize=(8, 3.5))
    plt.plot(w["step"], w["recovery_lag"], marker="o", linestyle="none", alpha=0.7, label="Estimated lag")
    plt.xlabel("Step")
    plt.ylabel("Steps to recover")
    plt.title("Estimated Fidelity Recovery Lag")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    rec_fig = outdir / "recovery_lag.png"
    plt.savefig(rec_fig, dpi=500)
    plt.close()

    print(f"✅ Saved processed CSV → {processed_csv}")
    print(f"✅ Saved figure → {bytes_fig}")
    print(f"✅ Saved figure → {rec_fig}")

if __name__ == "__main__":
    main()
