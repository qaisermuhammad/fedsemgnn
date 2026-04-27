#plot_fidelity_vs_gcn.py

#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

TRACE_FILE = "results/fedsemgnn_trace.json"
OUT_FILE   = "results/processed/fidelity_vs_gcn.png"
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)


with open(TRACE_FILE) as f:
    data = json.load(f)


steps = [entry["Step"] for entry in data]
gcn_ms = [entry["SystemMetrics"]["GCN_ms"] for entry in data]
fidelity = [entry["SystemMetrics"]["Fidelity_pct"] for entry in data]

# Plot
plt.figure(figsize=(8,5))
plt.scatter(gcn_ms, fidelity, color="#2c7fb8", alpha=0.6, s=28)
plt.title("Semantic Fidelity vs GCN Execution Time", fontsize=14)
plt.xlabel("GCN Latency (ms)", fontsize=12)
plt.ylabel("Semantic Fidelity", fontsize=12)
plt.grid(alpha=0.3)

# Annotate extreme outliers
for s, g, f in zip(steps, gcn_ms, fidelity):
    if g > 2.0 or f < 0.7:
        plt.annotate(f"Step {s}", xy=(g,f), textcoords="offset points", xytext=(5,-8), fontsize=8, color="#333")

plt.tight_layout()
plt.savefig(OUT_FILE, dpi=500)
plt.show()
