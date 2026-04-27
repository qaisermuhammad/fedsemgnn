import pandas as pd

lat = pd.read_csv("results/processed/substep_latency.csv")
es = pd.read_csv("results/processed/trace_edge_servers.csv")

server5 = es[es["ID"] == 5]
merged = pd.merge(server5, lat, on="Step")

# Show steps where GCN_ms was unusually high
print(merged[merged["GCN_ms"] > 2.0][["Step", "GCN_ms", "CPU", "OngoingMigrations"]])
