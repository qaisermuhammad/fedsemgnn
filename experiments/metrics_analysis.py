# metrics_analysis.py

import pandas as pd
import matplotlib.pyplot as plt

# Paths
METRICS_CSV = "results/processed/trace_metrics.csv"
OUT_DIR     = "results/processed"

# 1) Load and peek
# Note: Metrics reflect GNN-based FedSemGNN (GraphConv encoder, semantic-aware placement)
metrics_df = pd.read_csv(METRICS_CSV)
print("\n=== Metrics Head ===")
print(metrics_df.head(), "\n")

# 2) Summary stats
print("=== Summary ===")
print(metrics_df.describe().round(2), "\n")

# 3) Reward & Power over time
plt.figure(figsize=(10, 4))
plt.plot(metrics_df.Step, metrics_df.Reward, label="Reward", color="green")
plt.plot(metrics_df.Step, metrics_df.Power,  label="Power (W)", color="orange")
plt.title("FedSemGNN: Reward & Power over Time")
plt.xlabel("Step")
plt.ylabel("Value")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/metrics_reward_power.png", dpi=500)
print("Saved plot to results/processed/metrics_reward_power.png")

# 4) Fidelity vs Latency
fig, ax1 = plt.subplots(figsize=(10,4))
ax1.plot(metrics_df.Step, metrics_df.Fidelity, color="blue", label="Fidelity")
ax1.set_xlabel("Step")
ax1.set_ylabel("Fidelity", color="blue")
ax1.tick_params(labelcolor="blue")

ax2 = ax1.twinx()
ax2.plot(metrics_df.Step, metrics_df.Latency_ms, color="red", label="Latency (ms)")
ax2.set_ylabel("Latency (ms)", color="red")
ax2.tick_params(labelcolor="red")

plt.title("Semantic Fidelity vs Latency Over Time")
plt.grid(alpha=0.3)
fig.tight_layout()
plt.savefig(f"{OUT_DIR}/metrics_fidelity_latency.png", dpi=500)
plt.show()
plt.close()
print("Saved plot to results/processed/metrics_fidelity_latency.png")
