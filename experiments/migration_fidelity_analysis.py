# migration_fidelity_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import ast
import os

# --- Paths ---
ES_PATH  = "results/processed/trace_edge_servers.csv"
METRICS  = "results/processed/trace_metrics.csv"
OUT_DIR  = "results/processed"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Step 1: Load data ---
print("Loading edge-server and metrics data...")
es_df  = pd.read_csv(ES_PATH)
metrics_df = pd.read_csv(METRICS)

# --- Step 2: Total migrations per step across all servers ---
print("Computing migration totals...")
mig_by_step = es_df.groupby("Step")["OngoingMigrations"].sum().reset_index()
mig_by_step.rename(columns={"OngoingMigrations": "TotalMigrations"}, inplace=True)

# --- Step 3: Join with metrics ---
joined_df = pd.merge(metrics_df, mig_by_step, on="Step")

# --- Step 4: Flag Server 5 activity ---
es_df["ServiceIDs"] = es_df["ServiceIDs"].apply(ast.literal_eval)
server5_steps = es_df[(es_df["ID"] == 5) & (es_df["ServiceIDs"].apply(len) > 0)]["Step"].unique()
joined_df["Server5Active"] = joined_df["Step"].isin(server5_steps)

# --- Step 5: Plot Fidelity vs Migrations vs Server 5 activity ---
fig, ax1 = plt.subplots(figsize=(10, 5))

# Fidelity curve
ax1.plot(joined_df["Step"], joined_df["Fidelity"], label="Fidelity", color="blue", linewidth=1.8)
ax1.set_ylabel("Fidelity", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")
ax1.set_xlabel("Step")

# Migration overlay
ax2 = ax1.twinx()
ax2.plot(joined_df["Step"], joined_df["TotalMigrations"], label="Total Migrations", color="orange", linewidth=1.5, linestyle="--")
ax2.set_ylabel("Migrations", color="orange")
ax2.tick_params(axis="y", labelcolor="orange")

# Server 5 active dots
active_steps = joined_df[joined_df["Server5Active"]]
ax1.scatter(active_steps["Step"], active_steps["Fidelity"], color="red", label="Server 5 Active", s=40)

plt.title("Semantic Fidelity & Migration Activity\nHighlighting Server 5 Engagement")
fig.tight_layout()
fig.legend(loc="upper right")
plt.grid(alpha=0.3)
plt.savefig(f"{OUT_DIR}/migration_fidelity_server5.png", dpi=500)
plt.show()
plt.close()

print("✅ Saved migration-fidelity diagnostic to results/processed/migration_fidelity_server5.png")
