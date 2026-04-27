#plot_step_latency.py

#!/usr/bin/env python3

#THIS GRAPH MUST BE CHECKED

import pandas as pd
import matplotlib.pyplot as plt
import os

CSV = "results/processed/substep_latency.csv"
PNG = "results/processed/substep_latency.png"
os.makedirs(os.path.dirname(PNG), exist_ok=True)

df = pd.read_csv(CSV)
print("Sub‐step latency stats (ms):")
print(df.describe().round(2), "\n")

plt.figure(figsize=(8,5))
for col, color in zip(
    ["GCN_ms", "Placement_ms", "Trace_ms"],
    ["#1f77b4", "#ff7f0e", "#2ca02c"]
):
    plt.hist(df[col], bins=30, alpha=0.5, label=col, color=color)

plt.xlabel("Duration (ms)")
plt.ylabel("Count")
plt.title("FedSemGNN Sub-Phase Execution Times")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(PNG, dpi=500)
plt.show()
