# server5_trace_analysis.py

import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np
import os

# Paths
ES_PATH   = "results/processed/trace_edge_servers.csv"
SVC_PATH  = "results/processed/trace_services_expanded.csv"
METRICS   = "results/processed/trace_metrics.csv"
OUT_DIR   = "results/processed"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Step 1: Load files ---
print("Loading trace datasets...")
es_df  = pd.read_csv(ES_PATH)
svc_df = pd.read_csv(SVC_PATH)
metrics_df = pd.read_csv(METRICS)

# --- Step 2: Clean ServiceIDs column and extract placements on Server 5 ---
print("Parsing ServiceIDs for Server 5...")
es_df["ServiceIDs"] = es_df["ServiceIDs"].apply(ast.literal_eval)
server5_df = es_df[(es_df["ID"] == 5) & (es_df["ServiceIDs"].apply(len) > 0)].copy()
print(f"Found {len(server5_df)} steps where Server 5 hosted services.\n")

# --- Step 3: Join with system-level metrics ---
server5_steps = server5_df["Step"].unique()
server5_metrics = metrics_df[metrics_df["Step"].isin(server5_steps)].copy()

# --- Step 4: Visualize Reward, Power, Fidelity during Server 5 activity ---
plt.figure(figsize=(10,4))
plt.plot(metrics_df["Step"], metrics_df["Reward"], label="Reward", color="gray", alpha=0.5)
plt.scatter(server5_metrics["Step"], server5_metrics["Reward"], color="green", label="Server 5 Active", s=40)
plt.xlabel("Step"); plt.ylabel("Reward")
plt.title("Reward Over Time – Highlighting Server 5 Usage")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/server5_reward_highlight.png", dpi=500)
plt.show()
plt.close()
print("✅ Saved reward plot with Server 5 highlights.")

# --- Step 5: Optionally extract service placements on Server 5 ---
svc_server5 = svc_df[
    (svc_df["AssignedTo"] == 5) & (svc_df["Step"].isin(server5_steps))
].copy()

svc_server5_out = f"{OUT_DIR}/server5_services.csv"
svc_server5.to_csv(svc_server5_out, index=False)
print(f"✅ Saved services assigned to Server 5 in {svc_server5_out}")

# --- Step 6: Print semantic stats ---
sem_cols = [c for c in svc_server5.columns if c.startswith("sem_")]
sem_mean = svc_server5[sem_cols].mean().round(3)
print("\nMean semantic vector for Server 5 assignments:")
print(sem_mean)

# --- Step 7: Compare fidelity when Server 5 is active ---
plt.figure(figsize=(10,4))
plt.plot(metrics_df["Step"], metrics_df["Fidelity"], label="Fidelity", color="blue", alpha=0.5)
plt.scatter(server5_metrics["Step"], server5_metrics["Fidelity"], color="red", label="Server 5 Active", s=40)
plt.xlabel("Step"); plt.ylabel("Fidelity")
plt.title("Fidelity Over Time – Highlighting Server 5 Usage")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/server5_fidelity_highlight.png", dpi=500)
plt.show()
plt.close()
print("✅ Saved fidelity plot with Server 5 highlights.")
