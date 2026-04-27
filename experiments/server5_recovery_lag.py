# server5_recovery_lag.py
#!/usr/bin/env python3

import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt
import os

# Paths
ES_PATH    = "results/processed/trace_edge_servers.csv"
METRICS    = "results/processed/trace_metrics.csv"
OUT_DIR    = "results/processed"
os.makedirs(OUT_DIR, exist_ok=True)

# Load data
es_df      = pd.read_csv(ES_PATH)
metrics_df = pd.read_csv(METRICS)

# Total migrations per step
es_df["ServiceIDs"] = es_df["ServiceIDs"].apply(ast.literal_eval)
mig_by_step = es_df.groupby("Step")["OngoingMigrations"].sum().rename("TotalMigrations").reset_index()
df = pd.merge(metrics_df, mig_by_step, on="Step")

# Server 5 active steps
server5_steps = sorted(es_df[(es_df.ID==5)&(es_df.ServiceIDs.map(len)>0)]["Step"].unique())

# Choose threshold = 90th percentile
q90 = df.TotalMigrations.quantile(0.90)
spike_df = df[df.TotalMigrations >= q90]
spike_steps = spike_df.Step.tolist()

# If no spikes at 90th pct, fallback to mean+std
if len(spike_steps)==0:
    mean = df.TotalMigrations.mean()
    std  = df.TotalMigrations.std()
    thr  = mean + std
    spike_df = df[df.TotalMigrations >= thr]
    spike_steps = spike_df.Step.tolist()
    print(f"No spikes at 90th pct ({q90:.1f}); fallback threshold mean+std={thr:.1f}")

print(f"Detected {len(spike_steps)} migration spikes")

# Compute lags: next Server5 step after each spike
lags = []
for s in spike_steps:
    idx = np.searchsorted(server5_steps, s)
    if idx < len(server5_steps):
        lags.append(server5_steps[idx] - s)
lags = np.array(lags)

if len(lags)==0:
    print("No recovery lags found (no Server5 after spikes).")
else:
    print("Recovery Lag Stats (steps):",
          f"mean={lags.mean():.1f}",
          f"median={np.median(lags):.1f}",
          f"min={lags.min()}",
          f"max={lags.max()}")

    # Plot histogram
    plt.figure(figsize=(8,4))
    plt.hist(lags, bins=20, color="#2c7fb8", edgecolor="white")
    plt.title("Server 5 Recovery Lag\n(Migration Spike → Server 5 Activation)")
    plt.xlabel("Lag (steps)")
    plt.ylabel("Count")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out_png = f"{OUT_DIR}/server5_recovery_lag.png"
    plt.savefig(out_png, dpi=500)
    plt.close()
    print(f"Saved lag histogram to {out_png}")
