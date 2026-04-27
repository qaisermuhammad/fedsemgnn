# edge_server_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import ast

# Paths
ES_CSV  = "results/processed/trace_edge_servers.csv"
OUT_DIR = "results/processed"

# 1) Load and peek
es_df = pd.read_csv(ES_CSV)
print("\n=== Edge Servers Head ===")
print(es_df.head(), "\n")

# 2) Parse ServiceIDs and count
es_df["ServiceIDs"]  = es_df["ServiceIDs"].apply(ast.literal_eval)
es_df["NumServices"] = es_df["ServiceIDs"].apply(len)
print("=== After parsing ServiceIDs ===")
print(es_df[["Step","ID","NumServices","OngoingMigrations"]].head(), "\n")

# 3) Summary per server
group = es_df.groupby("ID").agg({
    "Power":           ["mean","max"],
    "NumServices":     ["mean","max"],
    "OngoingMigrations":["mean","max"]
}).round(2)
print("=== Per-Server Summary ===")
print(group, "\n")

# 4) Plot per-server power
plt.figure(figsize=(10, 5))
for sid, sub in es_df.groupby("ID"):
    plt.plot(sub.Step, sub.Power, label=f"ID={sid}")
plt.title("Per-Server Power Over Time")
plt.xlabel("Step")
plt.ylabel("Power (W)")
plt.legend(ncol=2, fontsize=8)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/es_power_over_time.png", dpi=500)
plt.show()
plt.close()
print("Saved plot to results/processed/es_power_over_time.png")

# 5) Services vs Migrations on server 5
sid = 5
sub = es_df[es_df.ID == sid]
fig, ax1 = plt.subplots(figsize=(8,4))
ax1.plot(sub.Step, sub.NumServices, color="tab:blue", label="NumServices")
ax1.set_ylabel("NumServices", color="tab:blue")
ax1.tick_params(labelcolor="tab:blue")
ax2 = ax1.twinx()
ax2.plot(sub.Step, sub.OngoingMigrations, color="tab:red", linestyle="--", label="Migrations")
ax2.set_ylabel("Migrations", color="tab:red")
ax2.tick_params(labelcolor="tab:red")
plt.title(f"Server {sid}: Services vs Migrations")
plt.grid(alpha=0.3)
fig.tight_layout()
plt.savefig(f"{OUT_DIR}/es5_services_migrations.png", dpi=500)
plt.show()
plt.close()
print("Saved plot to results/processed/es5_services_migrations.png")
