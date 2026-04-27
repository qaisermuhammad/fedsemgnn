#!/usr/bin/env python3
# migration_turbulence_and_outliers.py

import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt
import os

# Paths
OUT_DIR        = "results/processed"
OUTLIERS_CSV   = f"{OUT_DIR}/spike_outliers.csv"
ES_PATH        = f"{OUT_DIR}/trace_edge_servers.csv"
METRICS_PATH   = f"{OUT_DIR}/trace_metrics.csv"

os.makedirs(OUT_DIR, exist_ok=True)

# 1) Load outlier spikes
outliers = pd.read_csv(OUTLIERS_CSV)
print(f"Loaded {len(outliers)} outlier spikes")

# 2) Load edge‐server and metrics data
es_df      = pd.read_csv(ES_PATH)
metrics_df = pd.read_csv(METRICS_PATH)

# 3) Parse ServiceIDs
es_df["ServiceIDs"] = es_df["ServiceIDs"].apply(ast.literal_eval)

# 4) Filter Server 5 rows at outlier steps
prof = es_df[(es_df.ID == 5) & (es_df.Step.isin(outliers.Step))][
    ["Step","Power","ServiceIDs","OngoingMigrations"]
].copy()
prof["NumServices"] = prof["ServiceIDs"].apply(len)
prof.drop(columns="ServiceIDs", inplace=True)

# 5) Merge in fidelity & total migrations & TI
#   compute total migrations
mig = es_df.groupby("Step")["OngoingMigrations"].sum().rename("TotalMigrations").reset_index()
#   merge metrics + migrations
df = pd.merge(metrics_df, mig, on="Step")
df["TI"] = df["TotalMigrations"] / df["Fidelity"].replace(0, np.nan)

prof = prof.merge(outliers[["Step","Lag"]], on="Step")
prof = prof.merge(df[["Step","Fidelity","TotalMigrations","TI"]], on="Step")

# 6) Save detailed profile
out_csv = f"{OUT_DIR}/outlier_profile.csv"
prof.to_csv(out_csv, index=False)
print(f"Saved detailed profile to {out_csv}\n")

# 7) Print summary stats by lag
print("=== Server 5 Load at Outlier Spikes by Lag ===")
summary = prof.groupby("Lag").agg({
    "Power": ["mean","max","min"],
    "NumServices": ["mean","max","min"],
    "TotalMigrations": "mean",
    "Fidelity": "mean",
    "TI": "mean"
}).round(2)
print(summary, "\n")

# 8) Plot Power & NumServices vs Lag
fig, ax1 = plt.subplots(figsize=(8,4))

# Power
ax1.plot(prof.Lag, prof.Power, 'o', color="tab:blue", label="Power (W)")
ax1.set_xlabel("Recovery Lag")
ax1.set_ylabel("Power (W)", color="tab:blue")
ax1.tick_params(labelcolor="tab:blue")

# NumServices
ax2 = ax1.twinx()
ax2.plot(prof.Lag, prof.NumServices, 'x', color="tab:green", label="NumServices")
ax2.set_ylabel("NumServices", color="tab:green")
ax2.tick_params(labelcolor="tab:green")

plt.title("Server 5 Load vs Recovery Lag (Outliers)")
fig.tight_layout()
plt.grid(alpha=0.3)
fig.legend(loc="upper right")
out_png = f"{OUT_DIR}/outlier_load_vs_lag.png"
plt.show()
plt.savefig(out_png, dpi=500)
plt.close()
print(f"Saved load vs lag plot to {out_png}")
