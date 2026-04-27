#!/usr/bin/env python3
# delta_bytes_vs_lag.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Paths
OUT_DIR      = "results/processed"
OUTLIERS_CSV = f"{OUT_DIR}/spike_outliers.csv"
METRICS_CSV  = f"{OUT_DIR}/trace_metrics.csv"

os.makedirs(OUT_DIR, exist_ok=True)

# 1) Load just Step & Lag from outliers
outliers = pd.read_csv(OUTLIERS_CSV, usecols=["Step","Lag"])
print(f"Loaded {len(outliers)} outlier spikes")

# 2) Load BytesExchanged from metrics
metrics = pd.read_csv(METRICS_CSV, usecols=["Step","BytesExchanged"])

# 3) Merge to get BytesExchanged at each outlier step
df = outliers.merge(metrics, on="Step", how="left")

# 4) Compute BytesExchanged at previous step
prev = metrics.copy()
prev["Step"] += 1
prev.rename(columns={"BytesExchanged":"BytesPrev"}, inplace=True)

df = df.merge(prev, on="Step", how="left")

# 5) ΔBytes = current - previous (or just current if no prev)
df["DeltaBytes"] = df["BytesExchanged"] - df["BytesPrev"].fillna(0)

# 6) Save combined data
out_csv = f"{OUT_DIR}/delta_bytes_lag.csv"
df.to_csv(out_csv, index=False)
print(f"Saved ΔBytes vs Lag data to {out_csv}")

# 7) Compute correlation
corr = df[["DeltaBytes","Lag"]].corr().iloc[0,1]
print(f"Correlation ΔBytes vs Lag: {corr:.3f}")

# 8) Plot ΔBytes vs Lag
plt.figure(figsize=(6,5))
plt.scatter(df["Lag"], df["DeltaBytes"], alpha=0.7, s=30, color="#237C9C")
plt.xlabel("Recovery Lag (steps)")
plt.ylabel("Δ Bytes Exchanged")
plt.title("ΔBytes vs Recovery Lag for Outlier Spikes")
plt.grid(alpha=0.3)
plt.tight_layout()
out_png = f"{OUT_DIR}/delta_bytes_vs_lag.png"
plt.savefig(out_png, dpi=500)
plt.show()
plt.close()
print(f"Saved plot to {out_png}")
